import React from "react"
import axios from "axios"


export default function AdvanceButton() {

    function trigger() {
        axios.post("http://192.168.178.48:5000/advance")
    }

    return (
        <button class="button-red" role="button" onClick={trigger}>Advance</button>
    )
}
