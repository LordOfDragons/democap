/**
 * MIT License
 * 
 * Copyright (c) 2022 DragonDreams (info@dragondreams.ch)
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#include "DEMoCapLiveLinkSource.h"

#include <sstream>

#include "Async/Async.h"
#include "Engine/Engine.h"
#include "ILiveLinkClient.h"
#include "LiveLinkSubjectSettings.h"
#include "DEMoCapLiveLink.h"
#include "DEMoCapLiveLinkSourceSettings.h"
#include "Misc/CoreDelegates.h"
#include "Misc/ScopeLock.h"
#include "Misc/App.h"
#include "Roles/LiveLinkAnimationRole.h"
#include "Roles/LiveLinkTransformRole.h"

#define LOCTEXT_NAMESPACE "FDEMoCapLiveLinkSource"

FDEMoCapLiveLinkSource::FDEMoCapLiveLinkSource(const FDEMoCapLiveLinkConnectionSettings &settings) :
pClient(nullptr),
pSourceType(LOCTEXT("SourceType_DEMoCap", "DEMoCap")),
pSourceMachineName(LOCTEXT("SourceMachineName_DEMoCap", "DEMoCap")),
pSourceStatus(LOCTEXT("SourceStatus_Disconnected", "Disconnected")),
pStopping(false),
pThread(nullptr),
pDeferredStartDelegateHandle(FCoreDelegates::OnEndFrame.AddRaw(this, &FDEMoCapLiveLinkSource::Start)),
pHostname(settings.Hostname),
pPort(settings.Port),
pUpdateRate(settings.UpdateRate),
pCriticalSection(std::make_unique<FCriticalSection>()),
pConnection(std::make_shared<FDEMoCapLiveLinkConnection>(*this)){
}

FDEMoCapLiveLinkSource::~FDEMoCapLiveLinkSource(){
	// This could happen if the object is destroyed before FCoreDelegates::OnEndFrame calls FDEMoCapLiveLinkSource::Start
	if(pDeferredStartDelegateHandle.IsValid()){
		FCoreDelegates::OnEndFrame.Remove(pDeferredStartDelegateHandle);
	}

	if(pClient){
		pClient->OnLiveLinkSubjectAdded().Remove(pOnSubjectAddedDelegate);
	}

	Stop();

	if(pThread){
		pThread->WaitForCompletion();
		delete pThread;
		pThread = nullptr;
	}

	pConnection.reset();
}

void FDEMoCapLiveLinkSource::ReceiveClient(ILiveLinkClient *client, FGuid sourceGuid){
	pClient = client;
	pSourceGuid = sourceGuid;
	
	pOnSubjectAddedDelegate = client->OnLiveLinkSubjectAdded().AddRaw(
		this, &FDEMoCapLiveLinkSource::OnLiveLinkSubjectAdded);
}

void FDEMoCapLiveLinkSource::InitializeSettings(ULiveLinkSourceSettings *settings){
}

void FDEMoCapLiveLinkSource::Update(){
	const double currentTime = FPlatformTime::Seconds();
	if(pLastUpdateTime){
		const double elapsed = currentTime - pLastUpdateTime;
		// TODO call update on connection
	}
	pLastUpdateTime = currentTime;
}

bool FDEMoCapLiveLinkSource::IsSourceStillValid() const{
	return !pStopping && pThread;
}

bool FDEMoCapLiveLinkSource::RequestSourceShutdown(){
	Stop();
	return true;
}

FText FDEMoCapLiveLinkSource::GetSourceType() const{
	return pSourceType;
}

FText FDEMoCapLiveLinkSource::GetSourceMachineName() const{
	return pSourceMachineName;
}

FText FDEMoCapLiveLinkSource::GetSourceStatus() const{
	const FScopeLock Lock(pCriticalSection.get());
	return pSourceStatus;
}

TSubclassOf<ULiveLinkSourceSettings> FDEMoCapLiveLinkSource::GetSettingsClass() const{
	return UDEMoCapLiveLinkSourceSettings::StaticClass();
}

void FDEMoCapLiveLinkSource::OnSettingsChanged(ULiveLinkSourceSettings *settings,
const FPropertyChangedEvent& propertyChangedEvent){
	ILiveLinkSource::OnSettingsChanged(settings, propertyChangedEvent);
}

// FRunnable interface
void FDEMoCapLiveLinkSource::Start(){
	check(pDeferredStartDelegateHandle.IsValid());

	FCoreDelegates::OnEndFrame.Remove(pDeferredStartDelegateHandle);
	pDeferredStartDelegateHandle.Reset();

	pThreadName = "DEMoCapLiveLink Connection ";
	pThreadName.AppendInt(FAsyncThreadIndex::GetNext());

	pThread = FRunnableThread::Create(this, *pThreadName, 128 * 1024,
		TPri_AboveNormal, FPlatformAffinity::GetPoolThreadMask());
}

void FDEMoCapLiveLinkSource::Stop(){
	pStopping = true;
}

uint32 FDEMoCapLiveLinkSource::Run(){
	pFrameCounter = 0;
	
	pSubjectActorAnimation = std::make_shared<FDEMoCapLiveLinkAnimationSubject>(*this, "Actor_Animation");
	pEncounterSubject(pSubjectActorAnimation->GetName());
	
	pSubjectActorTransform = std::make_shared<FDEMoCapLiveLinkTransformSubject>(*this, "Actor_Transform");
	pEncounterSubject(pSubjectActorTransform->GetName());

	const double updateInterval = 1.0 / (double)pUpdateRate;
	const double reconnectDelay = 3.0;

	double startTime = FApp::GetCurrentTime() - updateInterval;
	double reconnectDelayStartTime = startTime - reconnectDelay - 1.0;
	
	while(!pStopping && pConnection){
		const double endTime = FApp::GetCurrentTime();
		const double elapsed = endTime - startTime;

		if(elapsed < updateInterval){
			FPlatformProcess::Sleep(0.001f);
			continue;
		}

		const int32 frameNumber = pFrameCounter;
		pFrameCounter = (pFrameCounter + 1) % 0x7fffffff;
		startTime = endTime;

		try{
			pConnection->Update((float)updateInterval);
		}catch(const std::exception &e){
			UE_LOG(LogDEMoCapLiveLink, Error, TEXT("Connection update failed: %s"), UTF8_TO_TCHAR(e.what()));
		}
		
		switch(pConnection->GetConnectionState()){
		case denConnection::ConnectionState::disconnected:{
			{
			const FScopeLock Lock(pCriticalSection.get());
			pConnected = false;
			if((endTime - reconnectDelayStartTime) < reconnectDelay){
				pSourceStatus = LOCTEXT("SourceStatus_DelayReconnect", "Delay Reconnect");
				break;
			}else{
				reconnectDelayStartTime = endTime;
				pSourceStatus = LOCTEXT("SourceStatus_Connecting", "Connecting");
			}
			}

			std::stringstream s;
			s << TCHAR_TO_UTF8(*pHostname) << ":" << (int)pPort;
			try{
				pConnection->ConnectTo(s.str());
			}catch(const std::exception &e){
				UE_LOG(LogDEMoCapLiveLink, Error, TEXT("ConnectTo failed: %s"), UTF8_TO_TCHAR(e.what()));
			}
			}break;

		case denConnection::ConnectionState::connecting:
			reconnectDelayStartTime = endTime;
			break;

		case denConnection::ConnectionState::connected:
			reconnectDelayStartTime = endTime;

			if(!pConnected){
				const FScopeLock Lock(pCriticalSection.get());
				pSourceStatus = LOCTEXT("SourceStatus_Connected", "Connected");
				pConnected = true;
			}

			pSubjectActorAnimation->Update(frameNumber);
			pSubjectActorTransform->Update(frameNumber);
		}
	}

	pSubjectActorAnimation.reset();
	pSubjectActorTransform.reset();

	return 0;
}

void FDEMoCapLiveLinkSource::OnLiveLinkSubjectAdded(FLiveLinkSubjectKey subjectKey){
	// Set rebroadcast to true for any new subjects
	if(pSubjectsToRebroadcast.Contains(subjectKey.SubjectName)){
		ULiveLinkSubjectSettings* const subjectSettings =
			Cast<ULiveLinkSubjectSettings>(pClient->GetSubjectSettings(subjectKey));
		if(subjectSettings){
			subjectSettings->bRebroadcastSubject = true;
		}
	}
}

void FDEMoCapLiveLinkSource::pEncounterSubject(const FName& name){
	if(pEncounteredSubjects.Contains(name)){
		return;
	}

	// If the LiveLink client already knows about this subject, then it must have been added via a preset
	// Only new subjects should be set to rebroadcast by default. Presets should respect the existing settings
	if(!pClient->GetSubjects(true, true).Contains(FLiveLinkSubjectKey(pSourceGuid, name))){
		pSubjectsToRebroadcast.Add(name);
	}
	
	pEncounteredSubjects.Add(name);
}

#undef LOCTEXT_NAMESPACE
