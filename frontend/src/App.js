import React, { useState, useEffect } from "react"
import axios from "axios"

import './App.css';


const flask = route => "http://192.168.178.48:5000" + route


function App() {

  return (
    <div className="flex flex-wrap">
      <Preview />
      <Controls />
    </div>
  )
}


const Preview = () => {
  return (
    <div className="h-screen grow flex justify-center bg-black">
      <img className="h-screen" src={flask("/preview")} alt="Preview of the current frame"></img>
    </div>
  )
}


const Controls = () => {

  const [isScanning, setIsScanning] = useState(true)
  const [path, setPath] = useState("")
  const [frames, setFrames] = useState(3800)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    axios.get(flask("/scan")).then(response => {
      setIsScanning(response.data.isScanning)
      setPath(response.data.path)
      setFrames(response.data.frames)
    })

    const sse = new EventSource(flask("/scan-stream"))
    sse.addEventListener("isScanning", e => setIsScanning(e.data === "True"))
    sse.addEventListener("path", e => setPath(e.data))
    sse.addEventListener("frames", e => setFrames(parseInt(e.data)))
    sse.addEventListener("progress", e => setProgress(parseInt(e.data)))
    sse.onerror = e => sse.close()  // TODO: Do something more intelligent

    return () => sse.close()
  }, [])

  const startScanStyle = "bg-blue-500 hover:bg-blue-700"
  const stopScanStyle = "bg-red-500 hover:bg-red-700"

  const startScan = () => axios.post(flask("/scan"), {path: path, frames: frames})
  const poweroff = () => axios.post(flask("/poweroff"))

  const onPathChange = event => setPath(event.target.value)
  const onFramesChange = event => setFrames(event.target.value)

  return (
    <div className="m-0 flex flex-col w-80">
      <ButtonGrid>
        <Toggle target={flask("/light")}>Light</Toggle>
        <Toggle target={flask("/advance")}>Advance</Toggle>
        <Toggle target={flask("/fastforward")}>Fast-Forward</Toggle>
        <Toggle target={flask("/focuszoom")}>Zoom</Toggle>
      </ButtonGrid>
      <label>Save Frames To</label>
      <input type="text" value={path} className="bg-green-200" disabled={isScanning} onChange={onPathChange}/>
      <label># Frames</label>
      <input type="text" value={frames} className="bg-green-200" disabled={isScanning} onChange={onFramesChange}/>
      <ProgressBar now={progress} max={frames}/>
      <button className={(isScanning ? stopScanStyle : startScanStyle) + " text-white font-bold py-2 px-4 rounded"} onClick={startScan}>{isScanning ? "Stop" : "Scan"}</button>
      <button className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded disabled:bg-gray-500" onClick={poweroff} disabled={isScanning}> ________poweroff</button>
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

  const [isEnabled, setIsEnabled] = useState(true)
  const [isActive, setIsActive] = useState(false)

  const inactiveStyle = "bg-blue-500 hover:bg-blue-700"
  const activeStyle = "bg-yellow-500 hover:bg-yellow-700"

  useEffect(() => {
    axios.get(props.target).then(response => {
      setIsEnabled(response.data.is_enabled)
      setIsActive(response.data.is_active)
    })

    const sse = new EventSource(props.target + "-stream")
    sse.addEventListener("is_enabled", e => setIsEnabled(e.data === "True"))
    sse.addEventListener("is_active", e => setIsActive(e.data === "True"))
    sse.onerror = e => sse.close()  // TODO: Do something more intelligent

    return () => sse.close()
  }, [props.target])

  const toggle = () => axios.post(props.target)

  return (
    <button className={"aspect-square " + (isActive ? activeStyle : inactiveStyle) + " text-white font-bold py-2 px-4 rounded disabled:bg-red-500"} onClick={toggle} disabled={!isEnabled}>{props.children}</button>
  )
}

const ProgressBar = (props) => {

  return (
    <div className="relative pt-1">
      <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-green-200">
        <div style={{width: `${props.now / props.max * 100}%`}} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-green-500"></div>
      </div>
    </div>
  )
}

export default App;
