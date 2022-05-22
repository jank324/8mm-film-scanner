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

  const scanButtonStartStyle = "bg-green-700 hover:bg-green-800 focus:ring-green-300 dark:bg-green-600 dark:hover:bg-green-700 dark:focus:ring-green-800"
  const scanButtonStopStyle = "bg-red-700 hover:bg-red-800 focus:ring-red-300 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900"

  const startScan = () => axios.post(flask("/scan"), {output_directory: outputDirectory, n_frames: nFrames})
  const poweroff = () => axios.post(flask("/poweroff"))

  const onOutputDirectoryChange = event => setOutputDirectory(event.target.value)
  const onNFramesChange = event => setNFrames(event.target.value)

  return (
    <div className="m-0 p-2 flex flex-col gap-4 w-80 dark:bg-gray-800">
      <ButtonGrid>
        <Toggle target={flask("/advance")}>🦦 Step</Toggle>
        <Toggle target={flask("/light")}>💡 Light</Toggle>
        <Toggle target={flask("/fastforward")}>🏎 Fast-Forward</Toggle>
        <Toggle target={flask("/focuszoom")}>🔍 Zoom</Toggle>
      </ButtonGrid>
      <ProgressBar now={currentFrameIndex + isScanning} max={nFrames}/>

      <div>
        <label for="n_frames" className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">Reel length</label>
        <input type="text" id="n_frames" className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="Number of frames" value={nFrames} required  disabled={isScanning} onChange={onNFramesChange} />
      </div>
      <div>
        <label for="output_directory" className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">Output directory</label>
        <input type="text" id="output_directory" className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="Directory to save scanned files to" value={outputDirectory} required disabled={isScanning} onChange={onOutputDirectoryChange} />
      </div>
      <button type="button" className={"focus:outline-none text-white focus:ring-4 font-medium rounded-lg text-sm px-5 py-2.5 " + (isScanning? scanButtonStopStyle : scanButtonStartStyle)} onClick={startScan}>{isScanning ? "⏹ Stop" : "🎥 Scan"}</button>
      <div className="flex flex-col-reverse justify-start items-end flex-grow">
        <button className="text-gray-900 bg-white hover:bg-gray-100 border border-gray-200 focus:ring-4 focus:outline-none focus:ring-gray-100 font-medium rounded-lg text-sm px-4 py-2.5 text-center inline-flex items-center dark:focus:ring-gray-600 dark:bg-gray-800 dark:border-gray-700 dark:text-white dark:hover:bg-gray-700 flex-grow-0" onClick={poweroff} disabled={isScanning}>😴 Power off</button>
      </div>
      
    </div>
  )
}


const ButtonGrid = (props) => {
  return (
    <div className="grid grid-cols-2 gap-2 pb-2 border-b-2 border-gray-200 dark:border-gray-700">
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
    <button className={"text-gray-900 bg-white hover:bg-gray-100 border border-gray-200 focus:ring-4 focus:outline-none focus:ring-gray-100 font-medium rounded-lg text-sm px-4 py-2.5 text-center inline-flex items-center dark:focus:ring-gray-600 dark:bg-gray-800 dark:border-gray-700 dark:text-white dark:hover:bg-gray-700 " + (isActive ? "text-red-500" : "text-[#bababa]")} onClick={toggle} disabled={!isEnabled}>{props.children}</button>
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
