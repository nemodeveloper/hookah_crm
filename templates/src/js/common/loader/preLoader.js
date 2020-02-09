/**
 * Created by nemodeveloper on 15.10.2016.
 */

var preLoaderId = 0;

function showPreLoader() {
    if (preLoaderId !== 0) {
        hidePreLoader();
    }
    preLoaderId = setInterval(function () {
        $("#container").LoadingOverlay("show");
    }, 1000);
}

function hidePreLoader() {
    clearTimeout(preLoaderId);
    $("#container").LoadingOverlay("hide", true);
}