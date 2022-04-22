import './App.css';

import {useState} from "react"
import axios from "axios"


function flask(route) {
  return "http://192.168.178.48:5000" + route
}


function App() {
  return (
    <div className="app">
      <Preview />
      <Controls />
    </div>
  )
}


function Preview() {
  return (
      <img className="preview" src={flask("/preview")}></img>
  )
}


function Controls() {

  return (
    <div className="controls">
      <AdvanceButton />
      <FastForwardButton />
      <ToggleLightButton />
      <FocusZoomButton />
    </div>
  )
}


function AdvanceButton() {

  function trigger() {
      axios.post(flask("/advance"))
  }

  return (
      <button onClick={trigger}>Advance</button>
  )
}


function FastForwardButton() {

  var isFastForwarding = false

  function trigger() {
      console.log(isFastForwarding)
      if (!isFastForwarding) {
          axios.post(flask("/fastforward"))
          isFastForwarding = true
      } else {
        axios.post(flask("/stop"))
          isFastForwarding = false
      }
  }

  return (
      <button onClick={trigger}>Fast-Forward</button>
  )
}


function ToggleLightButton() {

  function trigger() {
    axios.post(flask("/togglelight"))
  }

  return (
    <button onClick={trigger}>Light</button>
  )
}


function FocusZoomButton() {

  function trigger() {
      axios.post(flask("/togglefocuszoom"))
  }

  return (
      <button onClick={trigger}>Focus Zoom</button>
  )
}


export default App;
