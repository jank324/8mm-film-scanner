import React from "react"

import AdvanceButton from "./AdvanceButton"
import FastForwardButton from "./FastForwardButton"
import FocusZoomButton from "./FocusZoomButton"


export default function Controls() {

  return (
    <div class="controls">
      <AdvanceButton />
      <FastForwardButton />
      <FocusZoomButton />
    </div>
  )
}
