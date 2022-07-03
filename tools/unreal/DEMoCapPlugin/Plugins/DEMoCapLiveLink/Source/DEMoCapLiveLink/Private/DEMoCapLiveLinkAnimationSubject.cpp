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

#include "ILiveLinkClient.h"
#include "DEMoCapLiveLinkSource.h"
#include "Roles/LiveLinkAnimationTypes.h"
#include "Roles/LiveLinkAnimationRole.h"

#define LOCTEXT_NAMESPACE "DEMoCapLiveLinkAnimationSubject"

FDEMoCapLiveLinkAnimationSubject::FDEMoCapLiveLinkAnimationSubject(
	FDEMoCapLiveLinkSource &source, const FName &name) :
pSource(source),
pName(name),
pBones(nullptr),
pBoneCount(0),
pRigChanged(true)
{
}

FDEMoCapLiveLinkAnimationSubject::~FDEMoCapLiveLinkAnimationSubject(){
	if(pBones){
		delete [] pBones;
		pBones = nullptr;
		pBoneCount = 0;
	}
}

void FDEMoCapLiveLinkAnimationSubject::Update(int frameNumber){
	if(pRigChanged){
		pRigChanged = false;
		pUpdateStaticData();
	}

	FLiveLinkFrameDataStruct frameData(FLiveLinkAnimationFrameData::StaticStruct());
	FLiveLinkAnimationFrameData* const animationFrameData = frameData.Cast<FLiveLinkAnimationFrameData>();
	
	animationFrameData->Transforms.Reserve(pBoneCount);

	if(pSource.GetConnection() && pSource.GetConnection()->pTestValue){
		double value = ((double)pSource.GetConnection()->pTestValue->GetValue()) / 60.0;
		value = value * 180.0 - 90.0;
		FQuat rotation(FVector(0.0, 0.0, 1.0), FMath::DegreesToRadians(value));
		pBones[0].transform.SetRotation(rotation);
		/*
		FVector location(pBones[0].transform.GetLocation());
		location.Z = ((double)pSource.GetConnection()->pTestValue->GetValue()) / 60.0;
		pBones[0].transform.SetLocation(location);
		*/
	}else{
		FQuat rotation(pBones[0].transform.GetRotation() * FQuat(FVector(0.0, 0.0, 1.0), FMath::DegreesToRadians(1)));
		pBones[0].transform.SetRotation(rotation);
	}

	int32 i;
	for(i=0; i<pBoneCount; i++){
		animationFrameData->Transforms.Push(pBones[i].transform);
	}

	pSource.GetClient()->PushSubjectFrameData_AnyThread({pSource.GetSourceGuid(), pName}, MoveTemp(frameData));
}

void FDEMoCapLiveLinkAnimationSubject::pUpdateStaticData(){
	// update internal data
	if(pBones){
		delete [] pBones;
		pBones = nullptr;
		pBoneCount = 0;
	}

	int32 i;

	pBones = new FBone[1];
	pBoneCount = 1;

	pBones[0].name = FName(TEXT("Hips"));
	pBones[0].parent = -1;
	pBones[0].transform = FTransform();

	// build static frame data
	FLiveLinkStaticDataStruct staticData(FLiveLinkSkeletonStaticData::StaticStruct());
	FLiveLinkSkeletonStaticData* animationStaticData = staticData.Cast<FLiveLinkSkeletonStaticData>();

	TArray<FName> boneNames;
	TArray<int32> boneParents;

	boneNames.Reserve(pBoneCount);
	boneParents.Reserve(pBoneCount);

	for(i=0; i<pBoneCount; i++){
		boneNames.Push(pBones[i].name);
		boneParents.Push(pBones[i].parent);
	}

	animationStaticData->SetBoneNames(boneNames);
	animationStaticData->SetBoneParents(boneParents);
	
	// send static frame data
	pSource.GetClient()->PushSubjectStaticData_AnyThread({pSource.GetSourceGuid(), pName},
		ULiveLinkAnimationRole::StaticClass(), MoveTemp(staticData));
}

#undef LOCTEXT_NAMESPACE
