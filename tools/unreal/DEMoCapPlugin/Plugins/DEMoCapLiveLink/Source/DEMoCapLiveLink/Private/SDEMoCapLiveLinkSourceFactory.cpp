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

#include "SDEMoCapLiveLinkSourceFactory.h"
#include "DEMoCapLiveLink.h"
#include "DEMoCapLiveLinkSourceSettings.h"

#include "Widgets/Input/SButton.h"
#include "Widgets/SBoxPanel.h"

#if WITH_EDITOR
#include "DetailLayoutBuilder.h"
#endif //WITH_EDITOR

#define LOCTEXT_NAMESPACE "SDEMoCapLiveLinkSourceFactory"

void SDEMoCapLiveLinkSourceFactory::Construct(const FArguments& args){
#if WITH_EDITOR
	OnConnectionSettingsAccepted = args._OnConnectionSettingsAccepted;

	FStructureDetailsViewArgs structureViewArgs;
	FDetailsViewArgs detailArgs;
	detailArgs.bAllowSearch = false;
	detailArgs.bShowScrollBar = false;

	FPropertyEditorModule& propertyEditor = FModuleManager::Get().
		LoadModuleChecked<FPropertyEditorModule>(TEXT("PropertyEditor"));

	pStructOnScope = MakeShared<FStructOnScope>(FDEMoCapLiveLinkConnectionSettings::StaticStruct());
	CastChecked<UScriptStruct>(pStructOnScope->GetStruct())->CopyScriptStruct(
		pStructOnScope->GetStructMemory(), &pConnectionSettings);
	pStructureDetailsView = propertyEditor.CreateStructureDetailView(
		detailArgs, structureViewArgs, pStructOnScope);

	ChildSlot
	[
		SNew(SVerticalBox)
		+SVerticalBox::Slot()
		.FillHeight(1.f)
		[
			pStructureDetailsView->GetWidget().ToSharedRef()
		]
		+ SVerticalBox::Slot()
		.HAlign(HAlign_Right)
		.AutoHeight()
		[
			SNew(SButton)
			.OnClicked(this, &SDEMoCapLiveLinkSourceFactory::OnSettingsAccepted)
			.Text(LOCTEXT("AddSource", "Add"))
		]
	];
#endif //WITH_EDITOR
}

FReply SDEMoCapLiveLinkSourceFactory::OnSettingsAccepted(){
#if WITH_EDITOR
	CastChecked<UScriptStruct>(pStructOnScope->GetStruct())->CopyScriptStruct(
		&pConnectionSettings, pStructOnScope->GetStructMemory());
	OnConnectionSettingsAccepted.ExecuteIfBound(pConnectionSettings);
#endif //WITH_EDITOR

	return FReply::Handled();
}

#undef LOCTEXT_NAMESPACE
