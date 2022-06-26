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

#include "DEMoCapLiveLinkSourceFactory.h"
#include "DEMoCapLiveLinkSource.h"
#include "SDEMoCapLiveLinkSourceFactory.h"

#define LOCTEXT_NAMESPACE "DEMoCapLiveLinkSourceFactory"

FText UDEMoCapLiveLinkSourceFactory::GetSourceDisplayName() const{
	return LOCTEXT("SourceDisplayName", "DEMoCapLiveLink Source");	
}

FText UDEMoCapLiveLinkSourceFactory::GetSourceTooltip() const{
	return LOCTEXT("SourceTooltip", "Connects to DEMoCap to transfer motion capture data");
}

ULiveLinkSourceFactory::EMenuType UDEMoCapLiveLinkSourceFactory::GetMenuType() const{
	return EMenuType::SubPanel;
}

TSharedPtr<SWidget> UDEMoCapLiveLinkSourceFactory::BuildCreationPanel(
FOnLiveLinkSourceCreated inOnLiveLinkSourceCreated) const{
	return SNew(SDEMoCapLiveLinkSourceFactory).OnConnectionSettingsAccepted(
		FOnDEMoCapLiveLinkConnectionSettingsAccepted::CreateUObject(
			this, &UDEMoCapLiveLinkSourceFactory::CreateSourceFromSettings, inOnLiveLinkSourceCreated));
}

TSharedPtr<ILiveLinkSource> UDEMoCapLiveLinkSourceFactory::CreateSource(
const FString& connectionString) const
{
	FDEMoCapLiveLinkConnectionSettings connectionSettings;
	if(!connectionString.IsEmpty()){
		FDEMoCapLiveLinkConnectionSettings::StaticStruct()->ImportText(
			*connectionString, &connectionSettings, nullptr, PPF_None,
			GLog, TEXT("UDEMoCapLiveLinkSourceFactory"));
	}
	return MakeShared<FDEMoCapLiveLinkSource>(connectionSettings);
}

void UDEMoCapLiveLinkSourceFactory::CreateSourceFromSettings(
FDEMoCapLiveLinkConnectionSettings connectionSettings,
FOnLiveLinkSourceCreated OnSourceCreated) const
{
	FString connectionString;
	FDEMoCapLiveLinkConnectionSettings::StaticStruct()->ExportText(
		connectionString, &connectionSettings, nullptr, nullptr, PPF_None, nullptr);

	TSharedPtr<FDEMoCapLiveLinkSource> SharedPtr = MakeShared<FDEMoCapLiveLinkSource>(connectionSettings);
	OnSourceCreated.ExecuteIfBound(SharedPtr, MoveTemp(connectionString));
}

#undef LOCTEXT_NAMESPACE
