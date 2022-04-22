import React from "react"
import axios from "axios"


export default function FastForwardButton() {

    var isFastForwarding = false

    function trigger() {
        console.log(isFastForwarding)
        if (!isFastForwarding) {
            axios.post("http://192.168.178.48:5000/fastforward")
            isFastForwarding = true
        } else {
            axios.post("http://192.168.178.48:5000/stop")
            isFastForwarding = false
        }
    }

    return (
        <button class="button-red" role="button" onClick={trigger}>Fast-Forward</button>
    )
}
