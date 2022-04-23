import React, { useState, useEffect } from "react"
import axios from "axios"

import './App.css';


const flask = route => "http://192.168.178.48:5000" + route


function App() {
  return (
    <div className="flex">
      <Preview />
      <Controls />
    </div>
  )
}


const Preview = () => {
  return (
    <div className="h-screen grow flex justify-center bg-black">
      <img className="h-screen" src={flask("/preview")}></img>
    </div>
  )
}


const Controls = (props) => {

  return (
    <div className="m-0 flex flex-col w-80">
      <ButtonGrid>
        <Toggle target={flask("/light")}>Light</Toggle>
        <Toggle target={flask("/advance")}>Advance</Toggle>
        <Toggle target={flask("/fastforward")}>Fast-Forward</Toggle>
        <Toggle target={flask("/focuszoom")}>Zoom</Toggle>
      </ButtonGrid>
    </div>
  )
}


const ButtonGrid = (props) => {
  return (
    <div className="grid grid-cols-4 gap-2 m-2">
      {props.children}
    </div>
  )
}


const Toggle = (props) => {

  const [enabled, setEnabled] = useState(true)
  const [on, turnOn] = useState(true)

  const toggle = () => axios.post(props.target)

  return (
    <button className="aspect-square bg-slate-300" onClick={toggle} disabled={!enabled}>{props.children}</button>
  )
}

export default App;
