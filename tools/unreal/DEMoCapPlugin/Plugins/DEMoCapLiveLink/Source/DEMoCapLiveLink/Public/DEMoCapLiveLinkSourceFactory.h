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

#include "LiveLinkSourceFactory.h"

#include "DEMoCapLiveLinkConnectionSettings.h"
#include "DEMoCapLiveLinkSourceFactory.generated.h"

UCLASS()
class DEMOCAPLIVELINK_API UDEMoCapLiveLinkSourceFactory : public ULiveLinkSourceFactory{
public:
	GENERATED_BODY()

	virtual FText GetSourceDisplayName() const override;
	virtual FText GetSourceTooltip() const override;
	virtual EMenuType GetMenuType() const override;

	virtual TSharedPtr<SWidget> BuildCreationPanel(
		FOnLiveLinkSourceCreated OnLiveLinkSourceCreated) const override;

	virtual TSharedPtr<ILiveLinkSource> CreateSource(
		const FString &connectionString) const override;

private:
	void CreateSourceFromSettings(FDEMoCapLiveLinkConnectionSettings connectionSettings,
		FOnLiveLinkSourceCreated OnSourceCreated) const;
};
