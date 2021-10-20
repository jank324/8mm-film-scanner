$(document).ready(function() {

    $("#advance_button").click(function() {
        $.post("/advance")
    })

    $("#focuszoom_button").click(function() {
        $.post("/togglefocuszoom")
    })

})
