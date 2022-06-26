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

#include "../ThirdParty/DENetwork/Include/denetwork/denLogger.h"
#include "../ThirdParty/DENetwork/Include/denetwork/message/denMessageReader.h"
#include "../ThirdParty/DENetwork/Include/denetwork/message/denMessageWriter.h"
#include "../ThirdParty/DENetwork/Include/denetwork/state/denState.h"
#include "../ThirdParty/DENetwork/Include/denetwork/value/denValueString.h"

#define LOCTEXT_NAMESPACE "DEMoCapLiveLinkConnection"

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
pSource(source)
{
	SetLogger(std::make_shared<Logger>());
}

FDEMoCapLiveLinkConnection::~FDEMoCapLiveLinkConnection(){
}

void FDEMoCapLiveLinkConnection::ConnectionEstablished(){
}

void FDEMoCapLiveLinkConnection::ConnectionFailed(ConnectionFailedReason reason){
}

void FDEMoCapLiveLinkConnection::ConnectionClosed(){
}

void FDEMoCapLiveLinkConnection::MessageReceived(const denMessage::Ref &message){
}

denState::Ref FDEMoCapLiveLinkConnection::CreateState(const denMessage::Ref &message, bool readOnly){
	// testing
	denMessageReader reader(message->Item());
	switch(reader.ReadByte()){
	case 1:
		pTestState = std::make_shared<denState>(true);
		pTestState->AddValue(std::make_shared<denValueString>());
		pTestValue = std::make_shared<denValueInt>(denValueIntegerFormat::sint16);
		pTestState->AddValue(pTestValue);
		return pTestState;
	}

	return nullptr;
}

#undef LOCTEXT_NAMESPACE
