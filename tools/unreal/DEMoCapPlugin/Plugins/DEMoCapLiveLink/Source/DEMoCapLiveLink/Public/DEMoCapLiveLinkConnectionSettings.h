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

#include "CoreMinimal.h"
#include "DEMoCapLiveLinkConnectionSettings.generated.h"

USTRUCT()
struct DEMOCAPLIVELINK_API FDEMoCapLiveLinkConnectionSettings
{
	GENERATED_BODY()

public:
	/** Host name of DEMoCap to connect to */
	UPROPERTY(EditAnywhere, Category = "Connection Settings")
	FString Hostname = FString(TEXT("localhost"));

	/** Port of DEMoCap to connect to */
	UPROPERTY(EditAnywhere, Category = "Connection Settings")
	uint16 Port = 3413;

	/** Update rate (in Hz) at which to deliver capture data */
	UPROPERTY(EditAnywhere, Category = "Connection Settings", meta = (ClampMin = 1, ClampMax = 90))
	uint32 UpdateRate = 30;
};
