$(document).ready(function() {

    $("#advance_button").click(function() {
        $.post("/advance", function() {
            $("#preview").attr("src", "/videostream")
        })
    })
    
})
