import React from "react"
import axios from "axios"


export default function FocusZoomButton() {

    function trigger() {
        axios.post("http://192.168.178.48:5000/togglefocuszoom")
    }

    return (
        <button class="button-red" role="button" onClick={trigger}>Focus Zoom</button>
    )
}
