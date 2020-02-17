/**
 * Created by nemodeveloper on 15.10.2016.
 */


function showPreLoader() {
    $("#container").LoadingOverlay("show", {'resizeInterval': 500});
}

function hidePreLoader() {
    $("#container").LoadingOverlay("hide", true);
}