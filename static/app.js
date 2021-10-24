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

    const ctx = document.getElementById('histogram').getContext('2d');
    const myChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: [1, 2, 3, 4, 5, 6],
            datasets: [{
                data: [21, 21, 19, 13, 21, 3],
                backgroundColor: "rgba(180, 180, 180, 0.2)",
                borderColor: "rgba(180, 180, 180, 1)",
                borderWidth: 1
            }, {
                data: [12, 19, 3, 5, 2, 3],
                backgroundColor: "rgba(255, 99, 132, 0.2)",
                borderColor: "rgba(255, 99, 132, 1)",
                borderWidth: 1
            }, {
                data: [7, 19, 5, 3, 12, 7],
                backgroundColor: "rgba(75, 192, 192, 0.2)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 1
            }, {
                data: [1, 1, 13, 12, 2, 3],
                backgroundColor: "rgba(54, 162, 235, 0.2)",
                borderColor: "rgba(54, 162, 235, 1)",
                borderWidth: 1
            }]
        }
    })

})
