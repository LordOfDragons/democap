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

#pragma once

#include "ILiveLinkSource.h"
#include "DEMoCapLiveLinkConnectionSettings.h"
#include "DEMoCapLiveLinkSourceSettings.h"
#include "Roles/LiveLinkAnimationTypes.h"
#include "Roles/LiveLinkTransformTypes.h"

#include "Delegates/IDelegateInstance.h"
#include "MessageEndpoint.h"
#include "IMessageContext.h"
#include "HAL/ThreadSafeBool.h"
#include "HAL/Runnable.h"

#include "DEMoCapLiveLinkAnimationSubject.h"
#include "DEMoCapLiveLinkTransformSubject.h"

#include "DEMoCapLiveLinkConnection.h"

struct UDEMoCapLiveLinkSettings;

class ILiveLinkClient;


class DEMOCAPLIVELINK_API FDEMoCapLiveLinkSource :
	public ILiveLinkSource, public FRunnable,
	public TSharedFromThis<FDEMoCapLiveLinkSource>{
public:
	FDEMoCapLiveLinkSource(const FDEMoCapLiveLinkConnectionSettings &connectionSettings);

	virtual ~FDEMoCapLiveLinkSource();

	// Begin ILiveLinkSource Interface
	
	virtual void ReceiveClient(ILiveLinkClient *client, FGuid sourceGuid) override;
	virtual void InitializeSettings(ULiveLinkSourceSettings *settings) override;
	virtual void Update() override;

	virtual bool IsSourceStillValid() const override;

	virtual bool RequestSourceShutdown() override;

	virtual FText GetSourceType() const override;
	virtual FText GetSourceMachineName() const override;
	virtual FText GetSourceStatus() const override;

	virtual TSubclassOf<ULiveLinkSourceSettings> GetSettingsClass() const override;

	virtual void OnSettingsChanged(ULiveLinkSourceSettings *settings,
		const FPropertyChangedEvent &propertyChangedEvent) override;

	// End ILiveLinkSource Interface

	// Begin FRunnable Interface

	virtual bool Init() override { return true; }
	virtual uint32 Run() override;
	void Start();
	virtual void Stop() override;
	virtual void Exit() override { }

	// End FRunnable Interface

	inline ILiveLinkClient *GetClient() const{ return pClient; }
	inline const FGuid &GetSourceGuid() const{ return pSourceGuid; }

	inline const FString &GetHostName() const{ return pHostname; }
	inline uint16 GetPort() const{ return pPort; }

	// connection to DEMoCap
	inline const FDEMoCapLiveLinkConnection::Ref &GetConnection() const{ return pConnection; }

	// subjects
	inline const FDEMoCapLiveLinkAnimationSubject::Ref &GetSubjectActorAnimation() const{ return pSubjectActorAnimation; }
	inline const FDEMoCapLiveLinkTransformSubject::Ref &GetSubjectActorTransform() const{ return pSubjectActorTransform; }

private:
	// Callback when the a livelink subject has been added
	void OnLiveLinkSubjectAdded(FLiveLinkSubjectKey subjectKey);

private:
	void pEncounterSubject(const FName &name);

	ILiveLinkClient *pClient;
	FGuid pSourceGuid;

	FMessageAddress pConnectionAddress;

	FText pSourceType;
	FText pSourceMachineName;
	FText pSourceStatus;
	
	FThreadSafeBool pStopping;
	FRunnableThread *pThread;
	FString pThreadName;
	
	// subject tracking
	TSet<FName> pEncounteredSubjects;
	TSet<FName> pSubjectsToRebroadcast;

	// Deferred start delegate handle.
	FDelegateHandle pDeferredStartDelegateHandle;

	// frame counter for data
	int32 pFrameCounter = 0;
	bool pConnected = false;

	// DEMoCap connection address
	FString pHostname = FString(TEXT("localhost"));
	uint16 pPort = 3413;
	uint32 pUpdateRate;

	const std::unique_ptr<FCriticalSection> pCriticalSection;

	// Delegate for when the LiveLink client has ticked
	FDelegateHandle pOnSubjectAddedDelegate;

	// Last update time
	double pLastUpdateTime = 0;

	// connection to DEMoCap
	FDEMoCapLiveLinkConnection::Ref pConnection;

	// subjects
	FDEMoCapLiveLinkAnimationSubject::Ref pSubjectActorAnimation;
	FDEMoCapLiveLinkTransformSubject::Ref pSubjectActorTransform;
};
