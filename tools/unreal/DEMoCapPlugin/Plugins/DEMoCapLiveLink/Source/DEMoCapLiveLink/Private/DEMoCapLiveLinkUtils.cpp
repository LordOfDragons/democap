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

#include "DEMoCapLiveLinkUtils.h"

#include <sstream>

#include "../ThirdParty/DENetwork/Include/denetwork/math/denVector3.h"
#include "../ThirdParty/DENetwork/Include/denetwork/math/denQuaternion.h"

#define LOCTEXT_NAMESPACE "FDEMoCapLiveLinkUtils"

std::string FDEMoCapLiveLinkUtils::convertBoneName(const std::string &name){
	std::stringstream converted;

	std::string::const_iterator iter;
	for(iter = name.cbegin(); iter != name.cend(); iter++){
		if(*iter == '.'){
			converted << '_';
		}else{
			converted << *iter;
		}
	}

	return converted.str();
}

// NOTE: dragengine -> unrealengine
// ue.x = de.z
// ue.y = de.x
// ue.z = de.y

FVector FDEMoCapLiveLinkUtils::convertPosition(const denVector3& position){
	// unreal units are cm, dragengine m
	return FVector(position.z * 100.0, position.x * 100.0, position.y * 100.0);
}

FQuat FDEMoCapLiveLinkUtils::convertOrientation(const denQuaternion& orientation){
	return FQuat(orientation.z, orientation.x, orientation.y, orientation.w);
}

FTransform FDEMoCapLiveLinkUtils::convertTransform(
const denVector3& position, const denQuaternion& orientation){
	return FTransform(convertOrientation(orientation),
		convertPosition(position), FVector(1.0, 1.0, 1.0));
}

FVector FDEMoCapLiveLinkUtils::convertBonePosition(const denVector3& position){
	// this one is tricky. unreal units are cm, dragengine m. but meshes are
	// typically scaled so we do not know what scaling for bones is correct.
	// for the time being keep the values unscaled
	return FVector(position.z, position.x, position.y);
}

FQuat FDEMoCapLiveLinkUtils::convertBoneOrientation(const denQuaternion& orientation){
	return FQuat(orientation.z, orientation.x, orientation.y, orientation.w);
}

FTransform FDEMoCapLiveLinkUtils::convertBoneTransform(
const denVector3& position, const denQuaternion& orientation){
	return FTransform(convertBoneOrientation(orientation),
		convertBonePosition(position), FVector(1.0, 1.0, 1.0));
}

#undef LOCTEXT_NAMESPACE
