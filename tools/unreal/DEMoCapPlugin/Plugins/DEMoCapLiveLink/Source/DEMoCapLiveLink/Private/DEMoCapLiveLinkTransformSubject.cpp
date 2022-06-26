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

#include "DEMoCapLiveLinkTransformSubject.h"

#include "ILiveLinkClient.h"
#include "DEMoCapLiveLinkSource.h"
#include "Roles/LiveLinkTransformTypes.h"
#include "Roles/LiveLinkTransformRole.h"

#define LOCTEXT_NAMESPACE "DEMoCapLiveLinkTransformSubject"

FDEMoCapLiveLinkTransformSubject::FDEMoCapLiveLinkTransformSubject(
	FDEMoCapLiveLinkSource &source, const FName &name) :
pSource(source),
pName(name),
pRequiresStaticDataUpdate(true)
{
}

FDEMoCapLiveLinkTransformSubject::~FDEMoCapLiveLinkTransformSubject(){
}

void FDEMoCapLiveLinkTransformSubject::Update(int frameNumber){
	if(pRequiresStaticDataUpdate){
		pRequiresStaticDataUpdate = false;
		pUpdateStaticData();
	}

	FLiveLinkFrameDataStruct frameData(FLiveLinkTransformFrameData::StaticStruct());
	FLiveLinkTransformFrameData* const transformData = frameData.Cast<FLiveLinkTransformFrameData>();

	FQuat rotation(pTransform.GetRotation() * FQuat(FVector(0.0, 0.0, 1.0), 0.5));
	pTransform.SetRotation(rotation);

	transformData->Transform = pTransform;

	// These don't change frame to frame, so they really should be in
	// static data. However, there is no MetaData in LiveLink static data :(
	/*
	transformData->MetaData.StringMetaData.Add
		(FName(TEXT("DeviceId")), FString::Printf(TEXT("%d"), Device.DeviceId));
	transformData->MetaData.StringMetaData.Add(
		FName(TEXT("DeviceType")), GetDeviceTypeName(Device.DeviceType));
	transformData->MetaData.StringMetaData.Add(
		FName(TEXT("DeviceControlId")), Device.SubjectName.ToString());
	*/

	pSource.GetClient()->PushSubjectFrameData_AnyThread({pSource.GetSourceGuid(), pName}, MoveTemp(frameData));

	/*
				FQuat Orientation;
				FVector Position;

					TransformFrameData->Transform = FTransform(Orientation, Position);

					Send(&FrameData, Device.SubjectName);
	*/
}

void FDEMoCapLiveLinkTransformSubject::pUpdateStaticData(){
	FLiveLinkStaticDataStruct staticData(FLiveLinkTransformStaticData::StaticStruct());

	pSource.GetClient()->PushSubjectStaticData_AnyThread({pSource.GetSourceGuid(), pName},
		ULiveLinkTransformRole::StaticClass(), MoveTemp(staticData));
}

#undef LOCTEXT_NAMESPACE
