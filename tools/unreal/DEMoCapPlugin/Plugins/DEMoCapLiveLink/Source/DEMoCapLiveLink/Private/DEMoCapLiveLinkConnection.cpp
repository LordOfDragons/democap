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

#include "DEMoCapLiveLinkConnection.h"
#include "DEMoCapLiveLinkSource.h"
#include "DEMoCapLiveLink.h"
#include "DEMoCapLiveLinkUtils.h"

#include "../ThirdParty/DENetwork/Include/denetwork/denLogger.h"
#include "../ThirdParty/DENetwork/Include/denetwork/message/denMessageReader.h"
#include "../ThirdParty/DENetwork/Include/denetwork/message/denMessageWriter.h"
#include "../ThirdParty/DENetwork/Include/denetwork/state/denState.h"
#include "../ThirdParty/DENetwork/Include/denetwork/value/denValueString.h"

#define LOCTEXT_NAMESPACE "FDEMoCapLiveLinkConnection"

class Logger : public denLogger{
public:
	virtual void Log(LogSeverity severity, const std::string &message){
		switch(severity){
		case LogSeverity::error:
			UE_LOG(LogDEMoCapLiveLink, Error, TEXT("%s"), UTF8_TO_TCHAR(message.c_str()));
			break;

		case LogSeverity::warning:
			UE_LOG(LogDEMoCapLiveLink, Warning, TEXT("%s"), UTF8_TO_TCHAR(message.c_str()));
			break;

		case LogSeverity::info:
			UE_LOG(LogDEMoCapLiveLink, Display, TEXT("%s"), UTF8_TO_TCHAR(message.c_str()));
			break;

		case LogSeverity::debug:
			UE_LOG(LogDEMoCapLiveLink, Log, TEXT("%s"), UTF8_TO_TCHAR(message.c_str()));
			break;
		}
	}
};

FDEMoCapLiveLinkConnection::FDEMoCapLiveLinkConnection(FDEMoCapLiveLinkSource &source) :
pSource(source),
pReady(false),
pSupportedFeatures(0),
pEnabledFeatures(0),
pFrameNumberWindowSize(180),
pLastFrameNumber(-1),
pSourceFrameCaptureBoneLayout(0),
pSourceFrameCaptureFrame(0)
{
	SetLogger(std::make_shared<Logger>());
}

FDEMoCapLiveLinkConnection::~FDEMoCapLiveLinkConnection(){
}

void FDEMoCapLiveLinkConnection::ConnectionEstablished(){
	UE_LOG(LogDEMoCapLiveLink, Display, TEXT("%s"), TEXT("Connection: Send ConnectRequest"));
	const denMessage::Ref message(denMessage::Pool().Get());
	{
	denMessageWriter writer(message->Item());
	writer.WriteByte(1); // Connect Request
	writer.Write("DEMoCap-Client-0", 16);
	writer.WriteUInt(pSupportedFeatures);
	writer.WriteString8("UnrealDEMoCapLiveLink");
	}
	SendReliableMessage(message);
}

void FDEMoCapLiveLinkConnection::ConnectionFailed(ConnectionFailedReason reason){
	switch(reason){
	case ConnectionFailedReason::timeout:
		UE_LOG(LogDEMoCapLiveLink, Error, TEXT("%s"), TEXT("ConnectionFailed: Timeout"));
		break;

	case ConnectionFailedReason::rejected:
		UE_LOG(LogDEMoCapLiveLink, Error, TEXT("%s"), TEXT("ConnectionFailed: Rejected"));
		break;

	case ConnectionFailedReason::noCommonProtocol:
		UE_LOG(LogDEMoCapLiveLink, Error, TEXT("%s"), TEXT("ConnectionFailed: No common protocol"));
		break;

	case ConnectionFailedReason::invalidMessage:
		UE_LOG(LogDEMoCapLiveLink, Error, TEXT("%s"), TEXT("ConnectionFailed: Invalid message"));
		break;

	case ConnectionFailedReason::generic:
	default:
		UE_LOG(LogDEMoCapLiveLink, Error, TEXT("%s"), TEXT("ConnectionFailed: Generic problem"));
	}

	pResetState();
}

void FDEMoCapLiveLinkConnection::ConnectionClosed(){
	UE_LOG(LogDEMoCapLiveLink, Display, TEXT("%s"), TEXT("ConnectionClosed"));
	pResetState();
}

void FDEMoCapLiveLinkConnection::MessageReceived(const denMessage::Ref &message){
	if(!pReady){
		denMessageReader reader(message->Item());
		if(reader.ReadByte() == 2){ // Connect Accepted
			pProcessConnectAccepted(reader);
		}
		return;
	}

	denMessageReader reader(message->Item());
	switch(reader.ReadByte()){
	case 3: // Actor Capture Bone Layout
		pProcessCaptureBoneLayout(reader);
		break;

	case 4: // Actor Capture Frame
		pProcessCaptureFrame(reader);
		break;
	}
}

denState::Ref FDEMoCapLiveLinkConnection::CreateState(const denMessage::Ref &message, bool readOnly){
	if(!pReady){
		return nullptr;
	}

	denMessageReader reader(message->Item());
	switch(reader.ReadByte()){
	case 1: // Record/Playback
		/*
		pTestState = std::make_shared<denState>(true);
		pTestState->AddValue(std::make_shared<denValueString>());
		pTestValue = std::make_shared<denValueInt>(denValueIntegerFormat::sint16);
		pTestState->AddValue(pTestValue);
		return pTestState;
		*/
		return nullptr;
	}

	return nullptr;
}

void FDEMoCapLiveLinkConnection::pResetState(){
	pReady = false;
	pEnabledFeatures = 0;
	pLastFrameNumber = -1;
	pCaptureBoneLayout.reset();
	pCaptureFrame.reset();
	pSourceFrameCaptureBoneLayout = 0;
	pSourceFrameCaptureFrame = 0;
}

bool FDEMoCapLiveLinkConnection::pIgnoreFrameNumber(int32 frameNumber) const{
	if(pLastFrameNumber != -1){
		int32 difference = frameNumber - pLastFrameNumber;
		if(difference < -32767){
			difference += 65536; // wrap around uint16
		}
		if(abs(difference) > pFrameNumberWindowSize || difference < 0){
			return true;
		}
	}
	return false;
}

void FDEMoCapLiveLinkConnection::pProcessConnectAccepted(denMessageReader &reader){
	UE_LOG(LogDEMoCapLiveLink, Display, TEXT("%s"), TEXT("Connection: Received ConnectAccepted"));
	char signature[16];
	reader.Read(signature, 16);
	if(strncmp(signature, "DEMoCap-Server-0", 16)){
		// not a DEMoCap server
		UE_LOG(LogDEMoCapLiveLink, Warning, TEXT("%s"), TEXT("Connection: Signature mismatch"));
		Disconnect();
		return;
	}
	
	pEnabledFeatures = reader.ReadUInt();
	if((pEnabledFeatures & pSupportedFeatures) != pEnabledFeatures){
		// something went wrong
		UE_LOG(LogDEMoCapLiveLink, Warning, TEXT("%s"), TEXT("Connection: Feature mismatch"));
		Disconnect();
		return;
	}

	UE_LOG(LogDEMoCapLiveLink, Display, TEXT("%s"), TEXT("Connection: Ready"));
	pReady = true;
}

void FDEMoCapLiveLinkConnection::pProcessCaptureBoneLayout(denMessageReader &reader){
	const FDEMoCapLiveLinkCaptureBoneLayout::Ref layout(std::make_unique<FDEMoCapLiveLinkCaptureBoneLayout>());
	layout->revision = reader.ReadByte();
	const int boneCount = (int)reader.ReadUShort();
	int i;

	layout->bones.Reserve(boneCount);

	for(i=0; i<boneCount; i++){
		FDEMoCapLiveLinkCaptureBoneLayout::SBone bone;
		bone.name = FName(FDEMoCapLiveLinkUtils::convertBoneName(reader.ReadString8()).c_str());
		bone.parent = (int)reader.ReadShort();

		const denVector3 bonePosition(reader.ReadVector3());
		const denQuaternion boneOrientation(reader.ReadQuaternion());
		bone.transform = FDEMoCapLiveLinkUtils::convertBoneTransform(bonePosition, boneOrientation);

		layout->bones.Push(bone);

		if(bone.parent == -1){
			layout->rootBones.Push(i);
		}
	}

	// finished reading message successfully so the bone layout can be stored
	pCaptureBoneLayout = layout;
	pSourceFrameCaptureBoneLayout = pSource.GetFrameCounter();
	UE_LOG(LogDEMoCapLiveLink, Display, TEXT("Connection: Capture Bone Layout: revision %d, bones %d"),
		(int)layout->revision, boneCount);
}

void FDEMoCapLiveLinkConnection::pProcessCaptureFrame(denMessageReader &reader){
	const int32 frameNumber = (int32)reader.ReadUShort();

	// check if this message is not old
	if(pIgnoreFrameNumber(frameNumber)){
		return;
	}
	pLastFrameNumber = frameNumber;
	
	// check if the revision matches
	const uint8 revision = reader.ReadByte();
	if(revision != pCaptureBoneLayout->revision){
		return;
	}

	// store capture frame
	const FDEMoCapLiveLinkCaptureFrame::Ref frame(std::make_unique<FDEMoCapLiveLinkCaptureFrame>());
	const int boneCount = pCaptureBoneLayout->bones.Num();
	const FVector unscaled(1, 1, 1);
	int i;

	const denVector3 position(reader.ReadVector3());
	frame->position = FDEMoCapLiveLinkUtils::convertPosition(position);

	const denQuaternion orientation(reader.ReadQuaternion());
	frame->orientation = FDEMoCapLiveLinkUtils::convertOrientation(orientation);

	frame->scale = reader.ReadFloat();

	frame->bones.Reserve(boneCount);

	for(i=0; i<boneCount; i++){
		const denVector3 bonePosition(reader.ReadVector3());
		const denQuaternion boneOrientation(reader.ReadQuaternion());

		const FTransform localTransform(FDEMoCapLiveLinkUtils::convertBoneTransform(bonePosition, boneOrientation));
		const FTransform &originTransform = pCaptureBoneLayout->bones[i].transform;

		FTransform uetransform;
		FTransform::Multiply(&uetransform, &localTransform, &originTransform);

		frame->bones.Push(uetransform);
	}

	// finished reading message successfully so the capture frame can be stored
	pCaptureFrame = frame;
	pSourceFrameCaptureFrame = pSource.GetFrameCounter();
}

#undef LOCTEXT_NAMESPACE
