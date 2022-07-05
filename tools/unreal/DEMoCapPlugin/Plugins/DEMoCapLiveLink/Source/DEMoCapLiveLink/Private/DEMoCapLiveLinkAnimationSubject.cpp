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

#include "DEMoCapLiveLinkAnimationSubject.h"
#include "DEMoCapLiveLinkCaptureBoneLayout.h"
#include "DEMoCapLiveLinkCaptureFrame.h"
#include "DEMoCapLiveLinkConnection.h"

#include "ILiveLinkClient.h"
#include "DEMoCapLiveLinkSource.h"
#include "Roles/LiveLinkAnimationTypes.h"
#include "Roles/LiveLinkAnimationRole.h"

#define LOCTEXT_NAMESPACE "DEMoCapLiveLinkAnimationSubject"

FDEMoCapLiveLinkAnimationSubject::FDEMoCapLiveLinkAnimationSubject(
	FDEMoCapLiveLinkSource &source, const FName &name) :
pSource(source),
pName(name),
pFrameCaptureBoneLayout(-1)
{
	SetRootBoneRotation(FRotator(0.0, 90.0, 0.0));
}

FDEMoCapLiveLinkAnimationSubject::~FDEMoCapLiveLinkAnimationSubject(){
}

void FDEMoCapLiveLinkAnimationSubject::SetRootBoneRotation(const FRotator &rotation){
	pRootBoneRotation = rotation;
}

void FDEMoCapLiveLinkAnimationSubject::Update(int frameNumber){
	const FDEMoCapLiveLinkConnection::Ref &connection = pSource.GetConnection();
	if(!connection || !connection->GetReady() || !connection->GetCaptureBoneLayout() || !connection->GetCaptureFrame()){
		return;
	}

	// check if capture bone layout changed
	const FDEMoCapLiveLinkCaptureBoneLayout &layout = *connection->GetCaptureBoneLayout();
	const FDEMoCapLiveLinkCaptureFrame &capture = *connection->GetCaptureFrame();

	if(connection->GetSourceFrameCaptureBoneLayout() != pFrameCaptureBoneLayout){
		pUpdateStaticData(layout);
		pFrameCaptureBoneLayout = connection->GetSourceFrameCaptureBoneLayout();
	}

	// update dynamic data
	FLiveLinkFrameDataStruct frameData(FLiveLinkAnimationFrameData::StaticStruct());
	FLiveLinkAnimationFrameData* const animationFrameData = frameData.Cast<FLiveLinkAnimationFrameData>();
	
	animationFrameData->Transforms = capture.bones;

	const int rootBoneCount = layout.rootBones.Num();
	int i;
	for(i=0; i<rootBoneCount; i++){
		animationFrameData->Transforms[i] = animationFrameData->Transforms[i] * pRootBoneTransform;
	}

	pSource.GetClient()->PushSubjectFrameData_AnyThread({pSource.GetSourceGuid(), pName}, MoveTemp(frameData));
}

void FDEMoCapLiveLinkAnimationSubject::pUpdateStaticData(const FDEMoCapLiveLinkCaptureBoneLayout &layout){
	// build static frame data
	FLiveLinkStaticDataStruct staticData(FLiveLinkSkeletonStaticData::StaticStruct());
	FLiveLinkSkeletonStaticData* animationStaticData = staticData.Cast<FLiveLinkSkeletonStaticData>();

	TArray<FName> boneNames;
	TArray<int32> boneParents;

	const int boneCount = layout.bones.Num();
	int i;

	boneNames.Reserve(boneCount);
	for(i=0; i<boneCount; i++){
		boneNames.Push(layout.bones[i].name);
	}

	boneParents.Reserve(boneCount);
	for(i=0; i<boneCount; i++){
		boneParents.Push(layout.bones[i].parent);
	}

	animationStaticData->SetBoneNames(boneNames);
	animationStaticData->SetBoneParents(boneParents);
	
	// send static frame data
	pSource.GetClient()->PushSubjectStaticData_AnyThread({pSource.GetSourceGuid(), pName},
		ULiveLinkAnimationRole::StaticClass(), MoveTemp(staticData));
}

#undef LOCTEXT_NAMESPACE
