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
  const [outputDirectory, setOutputDirectory] = useState("")
  const [nFrames, setNFrames] = useState(3800)
  const [currentFrameIndex, setCurrentFrameIndex] = useState(0)

  useEffect(() => {
    axios.get(flask("/scan")).then(response => {
      setIsScanning(response.data.is_scanning)
      setOutputDirectory(response.data.output_directory)
      setNFrames(response.data.n_frames)
    })

    const sse = new EventSource(flask("/scan-stream"))
    sse.addEventListener("is_scanning", e => setIsScanning(e.data === "True"))
    sse.addEventListener("output_directory", e => setOutputDirectory(e.data))
    sse.addEventListener("n_frames", e => setNFrames(parseInt(e.data)))
    sse.addEventListener("current_frame_index", e => setCurrentFrameIndex(parseInt(e.data)))
    sse.onerror = e => sse.close()  // TODO: Do something more intelligent

    return () => sse.close()
  }, [])

  const startScanStyle = "bg-blue-500 hover:bg-blue-700"
  const stopScanStyle = "bg-red-500 hover:bg-red-700"

  const startScan = () => axios.post(flask("/scan"), {output_directory: outputDirectory, n_frames: nFrames})
  const poweroff = () => axios.post(flask("/poweroff"))

  const onOutputDirectoryChange = event => setOutputDirectory(event.target.value)
  const onNFramesChange = event => setNFrames(event.target.value)

  return (
    <div className="m-0 flex flex-col w-80 bg-[#0e0e0e]">
      <ButtonGrid>
        <Toggle target={flask("/advance")}>🦦 Step</Toggle>
        <Toggle target={flask("/light")}>💡 Light</Toggle>
        <Toggle target={flask("/fastforward")}>🏎 Fast-Forward</Toggle>
        <Toggle target={flask("/focuszoom")}>🔍 Zoom</Toggle>
      </ButtonGrid>
      <label className="select-none">Save Frames To</label>
      <input type="text" value={outputDirectory} className="bg-green-200" disabled={isScanning} onChange={onOutputDirectoryChange}/>
      <label className="select-none"># Frames</label>
      <input type="text" value={nFrames} className="bg-green-200" disabled={isScanning} onChange={onNFramesChange}/>
      <ProgressBar now={currentFrameIndex + isScanning} max={nFrames}/>
      <button className={(isScanning ? stopScanStyle : startScanStyle) + " text-white font-bold py-2 px-4 rounded"} onClick={startScan}>{isScanning ? "Stop" : "Scan"}</button>
      <button className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded disabled:bg-gray-500" onClick={poweroff} disabled={isScanning}> ________poweroff</button>
    </div>
  )
}


const ButtonGrid = (props) => {
  return (
    <div className="grid grid-cols-2 gap-2 m-2">
      {props.children}
    </div>
  )
}


const Toggle = (props) => {

  const [isEnabled, setIsEnabled] = useState(true)
  const [isActive, setIsActive] = useState(false)

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
    <button className={"bg-gradient-to-b from-[#1d1e22] to-[#16191d] font-bold text-center py-2 px-2 rounded-lg shadow-md shadow-black active:shadow-none hover:border-2 disabled:bg-red-500 " + (isActive ? "text-red-500" : "text-[#bababa]")} onClick={toggle} disabled={!isEnabled}>{props.children}</button>
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
