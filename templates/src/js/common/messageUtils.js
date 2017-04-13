/**
 * Created by nemodeveloper on 13.04.2017.
 */

var SUCCESS_MESSAGE_TYPE = 'success';
var WARNING_MESSAGE_TYPE = 'warning';
var ERROR_MESSAGE_TYPE = 'error';

function getMessageElem()
{
    return $('.messagelist');
}

function showMessage(type, message, needClear) {
    var messages = getMessageElem();
    if (needClear)
        clearMessages();

    messages.append(
        $('<li>', {
            class: type,
            text: message
        })
    );
}

function clearMessages() {
    getMessageElem().html('');
}
