$(document).ready(function() {
    $("#light_button").click(function() {
        $.post("/light")
    })
    
    $("#advance_button").click(function() {
        $.post("/advance", function() {
            $("#preview").attr("src", "/videostream")
        })
    })
})
