isFastForwarding = false

$(document).ready(function() {

    $("#advance_button").click(function() {
        $.post("/advance")
    })

    $("#fastforward_button").click(function() {
        if (!isFastForwarding) {
            isFastForwarding = true
            $.post("/fastforward")
            $("#fastforward_button").html("Stop")
        } else {
            isFastForwarding = false
            $.post("/stop")
            $("#fastforward_button").html("Fast-Forward")
        }
    })

    $("#focuszoom_button").click(function() {
        $.post("/togglefocuszoom")
    })

    const counterSource = new EventSource("/counter")
    counterSource.onmessage = function(e) {
        console.log("Received message for counter")
        $("#counter_label").text(e.data)
    }

})
