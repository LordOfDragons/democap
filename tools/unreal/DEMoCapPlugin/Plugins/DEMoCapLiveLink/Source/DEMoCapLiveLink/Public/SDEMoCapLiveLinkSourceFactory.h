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

#include "DEMoCapLiveLinkConnectionSettings.h"
#include "Widgets/SCompoundWidget.h"
#include "Widgets/DeclarativeSyntaxSupport.h"

#if WITH_EDITOR
#include "IStructureDetailsView.h"
#endif //WITH_EDITOR

#include "Input/Reply.h"

struct FDEMoCapLiveLinkConnectionSettings;

DECLARE_DELEGATE_OneParam(FOnDEMoCapLiveLinkConnectionSettingsAccepted, FDEMoCapLiveLinkConnectionSettings);

class SDEMoCapLiveLinkSourceFactory : public SCompoundWidget{
	SLATE_BEGIN_ARGS(SDEMoCapLiveLinkSourceFactory)
	{}
		SLATE_EVENT(FOnDEMoCapLiveLinkConnectionSettingsAccepted, OnConnectionSettingsAccepted)
	SLATE_END_ARGS()

	void Construct(const FArguments &args);


private:
	FDEMoCapLiveLinkConnectionSettings pConnectionSettings;

#if WITH_EDITOR
	TSharedPtr<FStructOnScope> pStructOnScope;
	TSharedPtr<IStructureDetailsView> pStructureDetailsView;
#endif //WITH_EDITOR

	FReply OnSettingsAccepted();
	FOnDEMoCapLiveLinkConnectionSettingsAccepted OnConnectionSettingsAccepted;
};
