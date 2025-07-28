# webrtc_debugging API Documentation

*Fetched using Context7 MCP server on 2025-07-28 10:00:43*

---

========================
CODE SNIPPETS
========================
TITLE: Handle TRTC Connection State Changes
DESCRIPTION: This snippet demonstrates how to listen for changes in the SDK's connection state to the Tencent Cloud using `trtc.on(TRTC.EVENT.CONNECTION_STATE_CHANGED)`. It allows monitoring transitions between 'DISCONNECTED', 'CONNECTING', and 'CONNECTED' states for UI updates.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/module-EVENT

LANGUAGE: javascript
CODE:
```
trtc.on(TRTC.EVENT.CONNECTION_STATE_CHANGED, event => {
  const prevState = event.prevState;
  const curState = event.state;
});
```

----------------------------------------

TITLE: Handle TRTC Connection State Changes
DESCRIPTION: This snippet shows how to subscribe to the `TRTC.EVENT.CONNECTION_STATE_CHANGED` event to monitor the SDK's connection state with Tencent Cloud. It provides access to `prevState` and `curState` for tracking connection transitions.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/module-EVENT

LANGUAGE: JavaScript
CODE:
```
trtc.on(TRTC.EVENT.CONNECTION_STATE_CHANGED, event => {
  const prevState = event.prevState;
  const curState = event.state;
});
```

----------------------------------------

TITLE: TRTC Connection State Changed Event (CONNECTION_STATE_CHANGED)
DESCRIPTION: Documents the `CONNECTION_STATE_CHANGED` event, which signals changes in the SDK's connection state to Tencent Cloud. It details the possible states ('DISCONNECTED', 'CONNECTING', 'CONNECTED') and the transitions between them, along with their meanings, allowing applications to display appropriate UI feedback.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/module-EVENT

LANGUAGE: APIDOC
CODE:
```
(static) CONNECTION_STATE_CHANGED
Default Value: 'connection-state-changed'

Description: SDK and Tencent Cloud connection state change event, you can use this event to listen to the overall connection state of the SDK and Tencent Cloud.

States:
  'DISCONNECTED': Connection disconnected
  'CONNECTING': Connecting
  'CONNECTED': Connected

State Change Meanings:
  DISCONNECTED -> CONNECTING: Trying to establish a connection, triggered when calling the enter room interface or when the SDK automatically reconnects.
  CONNECTING -> DISCONNECTED: Connection establishment failed, triggered when calling the exit room interface to interrupt the connection or when the connection fails after SDK retries.
  CONNECTING -> CONNECTED: Connection established successfully, triggered when the connection is successful.
  CONNECTED -> DISCONNECTED: Connection interrupted, triggered when calling the exit room interface or when the connection is disconnected due to network anomalies.
```

----------------------------------------

TITLE: TRTC Room and Connection Management API Updates
DESCRIPTION: This section covers updates to TRTC Web SDK APIs related to joining rooms, managing user roles, and monitoring connection states. It highlights optimizations for room entry time and improved event emission for connection status changes.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-01-info-changelog

LANGUAGE: APIDOC
CODE:
```
enterRoom(options: { roomId: string, userId: string, userSig: string, role?: string }): Promise<void>
  - Purpose: Joins a TRTC room. Optimized for reduced entry time.
  - Parameters:
    - roomId: The ID of the room to join.
    - userId: The user's unique ID.
    - userSig: User signature for authentication.
    - role: Optional role for the user (e.g., 'anchor', 'audience').

switchRole(role: string, privateMapKey?: string): Promise<void>
  - Purpose: Changes the user's role within the current room.
  - Parameters:
    - role: The new role to assume.
    - privateMapKey: Optional, can be updated when switching roles.

TRTC.EVENT.CONNECTION_STATE_CHANGED: string
  - Purpose: Event indicating changes in the SDK's connection state to the TRTC server.
  - States: Includes 'CONNECTING' state.
```

----------------------------------------

TITLE: Handle TRTC Audio Playback State Changes
DESCRIPTION: This snippet illustrates how to listen for `TRTC.EVENT.AUDIO_PLAY_STATE_CHANGED` events, logging the user ID, playback state, and the reason for the state change for both local and remote users. This helps in monitoring and debugging audio playback issues.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/module-EVENT

LANGUAGE: JavaScript
CODE:
```
trtc.on(TRTC.EVENT.AUDIO_PLAY_STATE_CHANGED, event => {
  console.log(`${event.userId} player is ${event.state} because of ${event.reason}`);
});
```

----------------------------------------

TITLE: TRTC Web SDK ERROR_CODE Module Constants
DESCRIPTION: Defines common error codes encountered in the TRTC Web SDK, providing insights into potential issues and their causes. These codes help in debugging and implementing robust error handling mechanisms.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-04-info-uplink-limits

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Constants:

INVALID_PARAMETER
  - Description: An invalid parameter was provided to an SDK method.
INVALID_OPERATION
  - Description: An invalid operation was attempted given the current SDK state.
ENV_NOT_SUPPORTED
  - Description: The current environment (browser, device) is not supported by the SDK.
DEVICE_ERROR
  - Description: A media device (camera, microphone) error occurred.
SERVER_ERROR
  - Description: A server-side error occurred during communication with the TRTC service.
OPERATION_FAILED
  - Description: An operation failed to complete successfully.
OPERATION_ABORT
  - Description: An operation was aborted.
UNKNOWN_ERROR
  - Description: An unknown or unclassified error occurred.
```

----------------------------------------

TITLE: Handle TRTC Web SDK Firewall Connection Errors
DESCRIPTION: This JavaScript snippet demonstrates how to listen for specific TRTC SDK errors (code 5501) that indicate firewall restrictions preventing media connection. It's intended to guide users to check their network or firewall settings for whitelisting necessary domains and ports.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-34-advanced-proxy

LANGUAGE: JavaScript
CODE:
```
trtc.on(TRTC.EVENT.ERROR, error => {
  // 用户网络防火墙受限，会导致无法正常进行音视频通话。
  // 此时引导用户更换网络 or 检查网络防火墙设置。
  if (error.code === TRTC.ERROR_CODE.OPERATION_FAILED && error.extraCode === 5501) {
  }
});
```

----------------------------------------

TITLE: RtcError Class API Reference
DESCRIPTION: API documentation for the RtcError class, detailing properties related to error codes, extra codes, function names, and error messages for debugging and handling real-time communication issues.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-27-advanced-small-stream

LANGUAGE: APIDOC
CODE:
```
RtcError Class:
  Properties:
    code: The error code.
    extraCode: Additional error code information.
    functionName: The name of the function where the error occurred.
    message: A descriptive error message.
    handler: The error handler.
```

----------------------------------------

TITLE: API Reference for ERROR_CODE Module Definitions
DESCRIPTION: Provides a comprehensive list of error codes returned by the Web SDK, indicating various issues that may arise during operation. These codes cover common problems such as invalid parameters, invalid operations, unsupported environments, device-related errors, server-side issues, and general operation failures or aborts. Understanding these codes is crucial for debugging and error handling.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-14-basic-set-video-profile

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Definitions:

INVALID_PARAMETER
INVALID_OPERATION
ENV_NOT_SUPPORTED
DEVICE_ERROR
SERVER_ERROR
OPERATION_FAILED
OPERATION_ABORT
UNKNOWN_ERROR
```

----------------------------------------

TITLE: Handle TRTC Network Quality Events
DESCRIPTION: This snippet illustrates how to monitor the local uplink and downlink network quality using `trtc.on(TRTC.EVENT.NETWORK_QUALITY)`. It provides metrics like network quality, RTT, and packet loss for both uplink and downlink connections.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/module-EVENT

LANGUAGE: javascript
CODE:
```
trtc.on(TRTC.EVENT.NETWORK_QUALITY, event => {
   console.log(`network-quality, uplinkNetworkQuality:${event.uplinkNetworkQuality}, downlinkNetworkQuality: ${event.downlinkNetworkQuality}`)
   console.log(`uplink rtt:${event.uplinkRTT} loss:${event.uplinkLoss}`)
   console.log(`downlink rtt:${event.downlinkRTT} loss:${event.downlinkLoss}`)
})
```

----------------------------------------

TITLE: TRTC Web SDK ERROR_CODE Module Definitions
DESCRIPTION: Defines common error codes encountered when using the TRTC Web SDK, indicating issues like invalid parameters, device errors, or server problems, which can be used for error handling and debugging.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-35-advanced-ai-denoiser

LANGUAGE: APIDOC
CODE:
```
Module: ERROR_CODE
Description: Defines numerical error codes returned by the SDK to indicate specific issues.

Error Codes:
- INVALID_PARAMETER: An invalid parameter was provided to an SDK method.
- INVALID_OPERATION: An operation was performed in an invalid state.
- ENV_NOT_SUPPORTED: The current environment is not supported by the SDK.
- DEVICE_ERROR: An error occurred with an audio or video device.
- SERVER_ERROR: A server-side error occurred.
- OPERATION_FAILED: The requested operation failed.
- OPERATION_ABORT: The operation was aborted.
- UNKNOWN_ERROR: An unknown error occurred.
```

----------------------------------------

TITLE: TRTC Web SDK: Stop Cross-Room Connections
DESCRIPTION: Use the `trtc.stopPlugin` method to terminate active cross-room connections. This can be used to stop a connection with a specific target room or to stop all cross-room connections initiated by the current user.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-30-advanced-cross-room-link

LANGUAGE: APIDOC
CODE:
```
trtc.stopPlugin('CrossRoom', { roomId: Number })
trtc.stopPlugin('CrossRoom')

Parameters:
  roomId: Number (Optional)
    Description: Target room ID to stop the connection with.
    
  strRoomId: String (Optional)
    Description: Target room string-type ID. Choose either roomId or strRoomId.
```

LANGUAGE: JavaScript
CODE:
```
await trtc.stopPlugin('CrossRoom', { roomId: 8888 }); // Stop the cross-room connection with the specified room
await trtc.stopPlugin('CrossRoom'); // Stop all cross-room connections initiated by the current user
```

----------------------------------------

TITLE: TRTC SDK CrossRoom Plugin Parameters for startPlugin
DESCRIPTION: This API documentation details the parameters used when calling `trtc.startPlugin('CrossRoom', ...)` to establish a cross-room connection. It specifies the types, requirements, and descriptions for `roomId`, `strRoomId`, and `userId`, which control whether the connection is room-level or user-level.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-30-advanced-cross-room-link

LANGUAGE: APIDOC
CODE:
```
startPlugin('CrossRoom', options)
  - options: Object containing connection parameters
    - roomId: Number
      - Required: No
      - Description: Target room ID (numeric).
    - strRoomId: String
      - Required: No
      - Description: Target room string-type ID. Use either `roomId` or `strRoomId`.
    - userId: String
      - Required: No
      - Description: Anchor ID in the target room. If not provided, it indicates a room-level connection; otherwise, it's a user-level connection.
```

----------------------------------------

TITLE: Handle TRTC Web SDK Firewall Errors
DESCRIPTION: This JavaScript snippet demonstrates how to listen for and identify specific firewall-related errors (error code 5501) from the TRTC Web SDK. It suggests guiding users to change networks or check firewall settings when this error occurs, indicating a failure in media connection establishment due to restrictions.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-34-advanced-proxy

LANGUAGE: JavaScript
CODE:
```
trtc.on(TRTC.EVENT.ERROR, error => {
  // User network firewall restrictions may cause audio and video calls to fail.
  // At this time, guide users to change networks or check network firewall settings.
  if (error.code === TRTC.ERROR_CODE.OPERATION_FAILED && error.extraCode === 5501) {
  }
});
```

----------------------------------------

TITLE: TRTC Web SDK Error Code Module Definitions
DESCRIPTION: Defines common error codes returned by the TRTC Web SDK, indicating issues such as invalid parameters, unsupported environments, device errors, and server-side problems, aiding in debugging and error handling.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-30-advanced-cross-room-link

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Definitions:

INVALID_PARAMETER: An invalid parameter was provided.
INVALID_OPERATION: An invalid operation was attempted.
ENV_NOT_SUPPORTED: The current environment is not supported.
DEVICE_ERROR: A media device error occurred.
SERVER_ERROR: A server-side error occurred.
OPERATION_FAILED: The operation failed.
OPERATION_ABORT: The operation was aborted.
UNKNOWN_ERROR: An unknown error occurred.
```

----------------------------------------

TITLE: Stop Cross-Room Co-anchoring with TRTC SDK
DESCRIPTION: This snippet demonstrates how to stop an active cross-room co-anchoring connection. You can either stop a specific connection by providing the `roomId` or stop all cross-room connections initiated by the current user by omitting the `roomId`.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-30-advanced-cross-room-link

LANGUAGE: JavaScript
CODE:
```
await trtc.stopPlugin('CrossRoom', { roomId: 8888 }); // Stop cross-room linking for the specified room
await trtc.stopPlugin('CrossRoom'); // Stop all cross-room linking initiated by the current user
```

LANGUAGE: APIDOC
CODE:
```
trtc.stopPlugin('CrossRoom', options):
  - Stops a cross-room co-anchoring connection.
  - Parameters:
    - roomId: Number (Optional) - The target room ID to stop the specific cross-room link.
    - strRoomId: String (Optional) - The target room string ID, choose one between `roomId` and `strRoomId`.
```

----------------------------------------

TITLE: Start Cross-Room Co-anchoring with TRTC SDK
DESCRIPTION: This snippet demonstrates how to initialize the `CrossRoom` plugin and initiate a cross-room connection. It covers both room-level linking (no `userId` specified) and user-level linking (with `userId`). Ensure your SDK version is v5.8.0 or higher.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-30-advanced-cross-room-link

LANGUAGE: JavaScript
CODE:
```
import { CrossRoom } from 'trtc-sdk-v5/plugins/cross-room';
const trtc = TRTC.create({ plugins: [CrossRoom] });
await trtc.enterRoom({ sdkAppId, userId: 'user1', userSig, roomId: 7777 });
// Connects user1 from current room 7777 with user2 from target room 8888. user2's stream will be pushed to room 7777, and user1's stream to room 8888.
await trtc.startPlugin('CrossRoom', {
  roomId: 8888,
  // Choose one between roomId and strRoomId
  // strRoomId: '8888'
  userId: 'user2' // If not passed, it's room-level cross-room linking
});
```

LANGUAGE: APIDOC
CODE:
```
trtc.startPlugin('CrossRoom', options):
  - Initiates a cross-room co-anchoring connection.
  - Parameters:
    - roomId: Number (Optional) - The target room ID.
    - strRoomId: String (Optional) - The target room string ID, choose one between `roomId` and `strRoomId`.
    - userId: String (Optional) - The target room's anchor ID. If not provided, it signifies room-level cross-room linking.
```

----------------------------------------

TITLE: Handle TRTC Network Quality Events
DESCRIPTION: This snippet demonstrates how to listen for and log network quality changes, including uplink/downlink quality, RTT, and packet loss, using the `TRTC.EVENT.NETWORK_QUALITY` event. It provides insights into the current network conditions for debugging and monitoring.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/module-EVENT

LANGUAGE: JavaScript
CODE:
```
trtc.on(TRTC.EVENT.NETWORK_QUALITY, event => {
   console.log(`network-quality, uplinkNetworkQuality:${event.uplinkNetworkQuality}, downlinkNetworkQuality: ${event.downlinkNetworkQuality}`)
   console.log(`uplink rtt:${event.uplinkRTT} loss:${event.uplinkLoss}`)
   console.log(`downlink rtt:${event.downlinkRTT} loss:${event.downlinkLoss}`)
})
```

----------------------------------------

TITLE: TRTC Web SDK Error Codes
DESCRIPTION: Enumerates common error codes encountered in the TRTC Web SDK, providing insights into potential issues like invalid parameters, device errors, or server problems. These codes help in debugging and handling exceptional conditions.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-13-basic-switch-camera-mic

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Error Codes:

- INVALID_PARAMETER: Invalid parameter provided.
- INVALID_OPERATION: Invalid operation performed.
- ENV_NOT_SUPPORTED: Environment not supported.
- DEVICE_ERROR: Device error occurred.
- SERVER_ERROR: Server error occurred.
- OPERATION_FAILED: Operation failed.
- OPERATION_ABORT: Operation aborted.
- UNKNOWN_ERROR: An unknown error occurred.
```

----------------------------------------

TITLE: QCloud TRTC Web SDK Error Codes
DESCRIPTION: Provides a comprehensive list of error codes returned by the QCloud TRTC Web SDK, detailing common issues such as invalid parameters, device errors, server errors, and unknown problems. Understanding these codes is essential for effective error handling and debugging.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-18-basic-debug

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Constants:

INVALID_PARAMETER
  - Description: An invalid parameter was provided.
INVALID_OPERATION
  - Description: An invalid operation was attempted.
ENV_NOT_SUPPORTED
  - Description: Current environment is not supported.
DEVICE_ERROR
  - Description: A media device error occurred.
SERVER_ERROR
  - Description: A server-side error occurred.
OPERATION_FAILED
  - Description: The operation failed.
OPERATION_ABORT
  - Description: The operation was aborted.
UNKNOWN_ERROR
  - Description: An unknown error occurred.
```

----------------------------------------

TITLE: TRTC Web SDK Error Code Module Definitions
DESCRIPTION: Defines various error codes returned by the TRTC Web SDK, indicating issues such as invalid parameters, device errors, server errors, and unknown problems. These codes help in debugging and handling exceptional conditions within the application.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-34-advanced-proxy

LANGUAGE: APIDOC
CODE:
```
Module: ERROR_CODE
  INVALID_PARAMETER: Invalid parameter provided.
  INVALID_OPERATION: Invalid operation performed.
  ENV_NOT_SUPPORTED: Environment not supported.
  DEVICE_ERROR: Device related error.
  SERVER_ERROR: Server related error.
  OPERATION_FAILED: Operation failed.
  OPERATION_ABORT: Operation aborted.
  UNKNOWN_ERROR: An unknown error occurred.
```

----------------------------------------

TITLE: API Reference for TRTC Web SDK Error Codes
DESCRIPTION: Lists common error codes returned by the TRTC Web SDK, providing insights into potential issues such as invalid parameters, device errors, or server-side problems. These codes help in debugging and handling exceptional conditions.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-17-basic-detect-volume

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Error Codes:

INVALID_PARAMETER: An invalid parameter was provided.
INVALID_OPERATION: An invalid operation was attempted.
ENV_NOT_SUPPORTED: The current environment is not supported.
DEVICE_ERROR: A media device error occurred.
SERVER_ERROR: A server-side error occurred.
OPERATION_FAILED: The operation failed.
OPERATION_ABORT: The operation was aborted.
UNKNOWN_ERROR: An unknown error occurred.
```

----------------------------------------

TITLE: TRTC Web SDK Device Error Code (5300) and Sub-categories
DESCRIPTION: Comprehensive documentation for the `DEVICE_ERROR` (5300) and its detailed `extraCode` sub-categories, outlining common causes, browser DOM exceptions, and recommended troubleshooting steps for device access issues in the TRTC Web SDK. Includes related API calls that may trigger this error.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/module-ERROR_CODE

LANGUAGE: APIDOC
CODE:
```
DEVICE_ERROR (Code: 5300)
  Default Value: 5300
  Description: Exception occurred when obtaining device or capturing microphone/camera/screen sharing.
  Related APIs: trtc.startLocalAudio, trtc.startLocalVideo, trtc.startScreenShare
  Suggestion: Guide the user to check whether the device has a camera and microphone, whether the system has authorized the browser, and whether the browser has authorized the page. It is recommended to increase the device detection process before entering the room to confirm whether the microphone and camera exist and can be captured normally before proceeding to the next call operation. Usually, this exception can be avoided after the device check. (Refer to: Check Environment and Device Before Calls)

  extraCode Sub-categories:

  5301: NotFoundError(DOMException)
    Reason: The media device type that meets the request parameters cannot be found (including: audio, video, screen sharing). For example: The PC does not have a camera, but the browser is requested to obtain a video stream, which will report this error.
    Suggestion: It is recommended to guide users to check the camera or microphone and other external devices required for the call before the call.

  5302: NotAllowedError(DOMException)
    Reason:
      - The user refused the microphone, camera, and screen sharing requests of the current browser instance.
      - The permission of camera/microphone/screen sharing has been denied by system.
    Suggestion:
      - Prompt the user to authorize the camera/microphone access before audio and video calls can be made.
      - If the browser permission is denied by the system, rtcError will have rtcError.handler method, which can be called to jump to the System Permission Setting APP, so as to facilitate the user to open the permission.

  5303: NotReadableError(DOMException)
    Reason: Although the user has authorized the use of the corresponding device, due to errors that occurred on some hardware, browser, or webpage levels on the operating system, or other applications occupying the device, the device cannot be accessed by the browser.
    Suggestion:
      - Handle according to the browser's error message, and prompt the user: "Unable to access the camera/microphone temporarily, please ensure that there are no other applications requesting access to the camera/microphone, and try again"
      - If this problem occurs with Windows Camera, the user will be directed to check whether the device is occupied. Only the camera of Windows system will be exclusive, but the microphone will not be exclusive.
      - If this error occurs with the microphone and camera of other systems, the user will be directed to check whether the device is normal or try to restart the browser.

  5304: OverconstrainedError(DOMException)
    Reason: The value of the cameraId/microphoneId parameter is invalid.
    Suggestion: Check whether cameraId/microphoneId is the value returned by the device information acquisition interface.

  5305: InvalidStateError(DOMException)
    Reason: The current page has not generated interaction, and the page is not fully activated.
    Suggestion: It is recommended to turn on the camera and microphone after the user has clicked on the page to generate interaction.

  5306: SecurityError(DOMException)
    Reason: The system security policy prohibits the use of the device.
    Suggestion: Check whether the system restricts the use of the device, and recommend turning on the camera and microphone after the user clicks on the page to generate interaction.

  5307: AbortError(DOMException)
    Reason: The device cannot be used due to some unknown reasons.
    Suggestion: It is recommended to replace the device or browser, and recheck whether the device is normal.

  5308: Camera capture exception
    Reason: Camera exception or the user manually closes the capture permission of the browser.
    Suggestion: Prompt the user that the camera capture is abnormal, and guide the user to check whether the camera is normal and whether there is a capture permission.
```

----------------------------------------

TITLE: TRTC Web SDK Error Codes
DESCRIPTION: Defines common error codes returned by the TRTC Web SDK, providing specific reasons for failures. These codes help in debugging and handling issues such as invalid parameters, unsupported environments, device-related problems, server errors, and general operation failures.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-21-advanced-auto-play-policy

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Definitions:

INVALID_PARAMETER: An invalid parameter was provided to an SDK method.
INVALID_OPERATION: An operation was attempted that is not valid in the current state.
ENV_NOT_SUPPORTED: The current environment (browser, device) is not supported by the SDK.
DEVICE_ERROR: An error occurred with a media device (e.g., camera, microphone).
SERVER_ERROR: An error occurred on the TRTC server side.
OPERATION_FAILED: A general operation failed to complete.
OPERATION_ABORT: An operation was aborted.
UNKNOWN_ERROR: An unknown or unclassified error occurred.
```

----------------------------------------

TITLE: Import and Register TRTC Debug Plugin (SDK <= 5.8.3)
DESCRIPTION: This JavaScript snippet demonstrates how to import and register the `Debug` plugin from `trtc-sdk-v5` for TRTC Web SDK versions 5.8.3 and older. This registration is necessary to enable debug functionalities, including log management and audio/video dumping, as the plugin was external in these versions.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-18-basic-debug

LANGUAGE: JavaScript
CODE:
```
import { Debug } from 'trtc-sdk-v5/plugins/debug';
let trtc = TRTC.create({ plugins: [Debug] });
```

----------------------------------------

TITLE: TRTC Web SDK ERROR_CODE Module Constants
DESCRIPTION: Defines common error codes encountered in the TRTC Web SDK, providing insights into various failure scenarios such as invalid parameters, device issues, and server errors. These codes help developers diagnose and troubleshoot problems during SDK integration and operation.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-24-advanced-network-quality

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module:
  INVALID_PARAMETER: Invalid parameter provided.
  INVALID_OPERATION: Invalid operation performed.
  ENV_NOT_SUPPORTED: Environment not supported.
  DEVICE_ERROR: Device error occurred.
  SERVER_ERROR: Server error occurred.
  OPERATION_FAILED: Operation failed.
  OPERATION_ABORT: Operation aborted.
  UNKNOWN_ERROR: An unknown error occurred.
```

----------------------------------------

TITLE: TRTC SDK Error Codes
DESCRIPTION: Enumerates common error codes returned by the TRTC SDK, indicating issues such as invalid parameters, unsupported environments, device failures, or server-side problems.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-00-info-update-guideline

LANGUAGE: APIDOC
CODE:
```
Module: ERROR_CODE
  INVALID_PARAMETER: Invalid parameter provided.
  INVALID_OPERATION: Invalid operation performed.
  ENV_NOT_SUPPORTED: Environment not supported.
  DEVICE_ERROR: Device related error.
  SERVER_ERROR: Server side error.
  OPERATION_FAILED: Operation failed.
  OPERATION_ABORT: Operation aborted.
  UNKNOWN_ERROR: Unknown error occurred.
```

----------------------------------------

TITLE: TRTC WebRTC SDK Error Codes
DESCRIPTION: Defines standard error codes returned by the TRTC WebRTC SDK, indicating various failure conditions. These include issues like invalid parameters, unsupported environments, device-related problems, server communication errors, and general operation failures.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-04-info-uplink-limits

LANGUAGE: APIDOC
CODE:
```
Module: ERROR_CODE
Error Codes:
  INVALID_PARAMETER: An invalid parameter was provided to an SDK method.
  INVALID_OPERATION: An operation was attempted that is not valid in the current state.
  ENV_NOT_SUPPORTED: The current browser or environment is not supported by the SDK.
  DEVICE_ERROR: A hardware device (e.g., camera, microphone) error occurred.
  SERVER_ERROR: An error occurred on the TRTC server side.
  OPERATION_FAILED: A general operation failed to complete successfully.
  OPERATION_ABORT: An ongoing operation was aborted.
  UNKNOWN_ERROR: An unspecified or unknown error occurred.
```

----------------------------------------

TITLE: RtcError Class API Reference
DESCRIPTION: Documents the RtcError class, detailing properties related to error codes, messages, and function names for debugging and error handling in the TRTC SDK.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-02-info-webrtc-issues

LANGUAGE: APIDOC
CODE:
```
RtcError Class Properties:

code: The error code.
extraCode: Additional error code information.
functionName: The name of the function where the error occurred.
message: The error message.
handler: The error handler.
```

----------------------------------------

TITLE: Handle TRTC Device Errors in JavaScript
DESCRIPTION: This JavaScript snippet demonstrates how to catch and handle device-related errors (e.g., camera/microphone not found, permission issues) when attempting to start local video using the TRTC Web SDK. It provides a switch statement to guide user interaction based on specific `extraCode` values.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/module-ERROR_CODE

LANGUAGE: javascript
CODE:
```
trtc.startLocalVideo(...).catch(function(rtcError) {
 if(rtcError.code == TRTC.ERROR_CODE.DEVICE_ERROR) {
   // 引导用户检查设备
   // 以下为可选代码
   switch(rtcError.extraCode) {
     case 5301:
       // 找不到摄像头或者麦克风，引导用户检查麦克风和摄像头是否正常。
       break;
     case 5302:
       if (error.handler) {
         // 提示用户系统关闭了浏览器的摄像头、麦克风、屏幕分享采集权限，即将跳转至系统权限设置 APP，请打开相关权限后，重启浏览器重试。
       } else {
         // 引导用户允许摄像头、麦克风、屏幕分享采集权限
       }
       break;
     // ...
   }
 }
})
```

----------------------------------------

TITLE: TRTC Web SDK EVENT Module Listeners
DESCRIPTION: Lists all events that can be listened to in the TRTC Web SDK, providing notifications for critical occurrences such as errors, user entry/exit, media availability changes, network quality updates, connection state changes, and device modifications.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-40-advanced-video-mixer

LANGUAGE: APIDOC
CODE:
```
EVENT Module Listeners:

ERROR: An error occurred.
AUTOPLAY_FAILED: Autoplay failed.
KICKED_OUT: User was kicked out.
REMOTE_USER_ENTER: A remote user entered the room.
REMOTE_USER_EXIT: A remote user exited the room.
REMOTE_AUDIO_AVAILABLE: Remote audio is available.
REMOTE_AUDIO_UNAVAILABLE: Remote audio is unavailable.
REMOTE_VIDEO_AVAILABLE: Remote video is available.
REMOTE_VIDEO_UNAVAILABLE: Remote video is unavailable.
AUDIO_VOLUME: Audio volume changed.
AUDIO_FRAME: Audio frame received.
NETWORK_QUALITY: Network quality changed.
CONNECTION_STATE_CHANGED: Connection state changed.
AUDIO_PLAY_STATE_CHANGED: Audio play state changed.
VIDEO_PLAY_STATE_CHANGED: Video play state changed.
SCREEN_SHARE_STOPPED: Screen sharing stopped.
DEVICE_CHANGED: Device changed.
PUBLISH_STATE_CHANGED: Publish state changed.
TRACK: Track event.
STATISTICS: Statistics updated.
SEI_MESSAGE: SEI message received.
CUSTOM_MESSAGE: Custom message received.
FIRST_VIDEO_FRAME: First video frame rendered.
```

----------------------------------------

TITLE: TRTC Web SDK ERROR_CODE Module Constants
DESCRIPTION: Enumerates common error codes encountered in the TRTC Web SDK's ERROR_CODE module. These codes help in identifying and troubleshooting issues such as invalid input parameters, incorrect operations, unsupported environments, device-related problems, server-side errors, general operation failures, aborted operations, and unknown errors.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/module-ERROR_CODE

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Constants:

INVALID_PARAMETER
  - Description: An invalid parameter was provided.
INVALID_OPERATION
  - Description: An invalid operation was attempted.
ENV_NOT_SUPPORTED
  - Description: The current environment is not supported.
DEVICE_ERROR
  - Description: A media device error occurred.
SERVER_ERROR
  - Description: A server-side error occurred.
OPERATION_FAILED
  - Description: The operation failed.
OPERATION_ABORT
  - Description: The operation was aborted.
UNKNOWN_ERROR
  - Description: An unknown error occurred.
```

----------------------------------------

TITLE: QCloud TRTC WebRTC v5 ERROR_CODE Module Definitions
DESCRIPTION: Enumerates common error codes encountered in the QCloud TRTC WebRTC v5 SDK, providing insights into potential issues like invalid parameters, device errors, or server problems. These codes help in debugging and handling error conditions gracefully.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-23-advanced-support-detection

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Definitions:

INVALID_PARAMETER: An invalid parameter was provided to an SDK method.
INVALID_OPERATION: An invalid operation was attempted given the current SDK state.
ENV_NOT_SUPPORTED: The current environment or browser is not supported by the SDK.
DEVICE_ERROR: A device-related error occurred (e.g., camera/microphone access issue).
SERVER_ERROR: A server-side error occurred during communication with TRTC services.
OPERATION_FAILED: The requested operation failed to complete.
OPERATION_ABORT: The operation was aborted, possibly by the user or system.
UNKNOWN_ERROR: An unspecified or unknown error occurred.
```

----------------------------------------

TITLE: TRTC Web SDK Event Listeners
DESCRIPTION: Lists all events that can be emitted by the TRTC Web SDK, allowing applications to react to changes in connection state, user presence, media availability, and more. Developers can subscribe to these events to implement dynamic UI updates and application logic.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-03-info-error-code-tips

LANGUAGE: APIDOC
CODE:
```
EVENT:
  ERROR
  AUTOPLAY_FAILED
  KICKED_OUT
  REMOTE_USER_ENTER
  REMOTE_USER_EXIT
  REMOTE_AUDIO_AVAILABLE
  REMOTE_AUDIO_UNAVAILABLE
  REMOTE_VIDEO_AVAILABLE
  REMOTE_VIDEO_UNAVAILABLE
  AUDIO_VOLUME
  AUDIO_FRAME
  NETWORK_QUALITY
  CONNECTION_STATE_CHANGED
  AUDIO_PLAY_STATE_CHANGED
  VIDEO_PLAY_STATE_CHANGED
  SCREEN_SHARE_STOPPED
  DEVICE_CHANGED
  PUBLISH_STATE_CHANGED
  TRACK
  STATISTICS
  SEI_MESSAGE
  CUSTOM_MESSAGE
  FIRST_VIDEO_FRAME
```

----------------------------------------

TITLE: TRTC Web SDK ERROR_CODE Module Constants
DESCRIPTION: Provides a comprehensive list of error codes returned by the TRTC Web SDK, indicating various issues such as invalid parameters, device errors, server problems, and unknown errors. These codes are essential for debugging and implementing robust error handling in applications.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/module-TYPE

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Constants:

INVALID_PARAMETER
  - Description: Error code for an invalid parameter provided to an SDK method.
INVALID_OPERATION
  - Description: Error code for an operation that is not valid in the current SDK state.
ENV_NOT_SUPPORTED
  - Description: Error code indicating that the current environment (browser, OS) is not supported.
DEVICE_ERROR
  - Description: Error code for issues related to audio or video devices.
SERVER_ERROR
  - Description: Error code for an error originating from the TRTC server.
OPERATION_FAILED
  - Description: General error code indicating an operation failed.
OPERATION_ABORT
  - Description: Error code indicating an operation was aborted.
UNKNOWN_ERROR
  - Description: Error code for an unspecified or unknown error.
```

----------------------------------------

TITLE: TRTC Web SDK: Dynamic Resolution Adjustment for Performance Issues
DESCRIPTION: Demonstrates how to handle performance-related errors (e.g., high latency) in the TRTC Web SDK by dynamically reducing video resolution and frame rate, or optionally disabling the beauty plugin, to optimize performance.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-28-advanced-beauty

LANGUAGE: JavaScript
CODE:
```
async function onError(error) {
  const { code } = error;
  if (code === 10000003 || code === 10000006) {
    // Reduce resolution and frame rate
    await trtc.updateLocalVideo({
      option: {
        profile: '480p_2'
      },
    });
    // await trtc.stopPlugin('Beauty'); // Or disable the plugin
  }
}
await trtc.startPlugin('Beauty', {
  ...// Other parameters
  onError,
});
```

----------------------------------------

TITLE: TRTC Web SDK Error Code Module Definitions
DESCRIPTION: Provides a comprehensive list of common error codes encountered when using the TRTC Web SDK. These codes help in diagnosing issues related to invalid parameters, unsupported environments, device malfunctions, server communication problems, and general operation failures. Understanding these codes is crucial for effective error handling and debugging.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-15-basic-dynamic-add-video

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Definitions:

INVALID_PARAMETER: Invalid parameter provided.
INVALID_OPERATION: Invalid operation performed.
ENV_NOT_SUPPORTED: Environment not supported.
DEVICE_ERROR: Device error occurred.
SERVER_ERROR: Server error occurred.
OPERATION_FAILED: Operation failed.
OPERATION_ABORT: Operation aborted.
UNKNOWN_ERROR: An unknown error occurred.
```

----------------------------------------

TITLE: TRTC Web SDK RtcError Object API Reference
DESCRIPTION: Defines the `RtcError` object, its constructor, static properties for error codes and messages, and a handler method for specific error recovery scenarios, such as device permission issues.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/RtcError

LANGUAGE: APIDOC
CODE:
```
RtcError
  - Description: RtcError error object, extends Error.
  - Constructor:
    new RtcError()
      - Description: Creates a new RtcError instance.
  - Extends: Error
  - Static Members:
    code (readonly)
      - Type: number
      - Description: Error code. See ErrorCode for detailed list.
    extraCode (readonly)
      - Type: number
      - Description: Extended error code. See ErrorCode for detailed list.
    functionName (readonly)
      - Type: string
      - Description: The name of the function that throws the error.
    message (readonly)
      - Type: string
      - Description: Error message.
    handler (readonly)
      - Type: Function
      - Description: Error handler for recovering from specific errors (e.g., device permission denied). Available since v5.2.0.
      - Usage Example:
        trtc.startLocalAudio().catch(error => {
         if (error.extraCode === 5302 && typeof error.handler === 'function') {
           // Prompt the user the browser permission(camera/microphone/screen sharing) has been denied by system. The browser will jump to the System Settings APP, please enable the relevant permissions!
           // Available in Windows and MacOS.
           error.handler();
         }
        })
```

----------------------------------------

TITLE: TRTC Web SDK Error Codes
DESCRIPTION: Provides a comprehensive list of error codes returned by the TRTC Web SDK, indicating various issues such as invalid parameters, invalid operations, unsupported environments, device errors, server errors, and general operation failures. These codes help in debugging and handling exceptional scenarios within the application.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-39-advanced-video-decoder

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Constants:
  INVALID_PARAMETER: An invalid parameter was provided.
  INVALID_OPERATION: An invalid operation was attempted.
  ENV_NOT_SUPPORTED: The current environment is not supported.
  DEVICE_ERROR: A device-related error occurred (e.g., camera/mic access).
  SERVER_ERROR: A server-side error occurred.
  OPERATION_FAILED: The operation failed.
  OPERATION_ABORT: The operation was aborted.
  UNKNOWN_ERROR: An unknown error occurred.
```

----------------------------------------

TITLE: Error Codes for TRTC Web SDK
DESCRIPTION: Defines a comprehensive list of error codes that can be returned by the TRTC Web SDK, indicating various issues from invalid parameters and operations to environment limitations, device failures, server-side problems, and general operation failures or aborts. These codes help developers diagnose and handle issues programmatically.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/module-EVENT

LANGUAGE: APIDOC
CODE:
```
Module: ERROR_CODE
  INVALID_PARAMETER: Invalid parameter provided
  INVALID_OPERATION: Invalid operation performed
  ENV_NOT_SUPPORTED: Environment not supported
  DEVICE_ERROR: Device error
  SERVER_ERROR: Server error
  OPERATION_FAILED: Operation failed
  OPERATION_ABORT: Operation aborted
  UNKNOWN_ERROR: Unknown error
```

----------------------------------------

TITLE: TRTC Web SDK EVENT Module Listeners
DESCRIPTION: Lists the events that can be listened to in the TRTC Web SDK, covering connection states, user presence, media availability, device changes, and more, allowing applications to react to SDK state changes.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-35-advanced-ai-denoiser

LANGUAGE: APIDOC
CODE:
```
Module: EVENT
Description: Defines events that the SDK dispatches, allowing applications to subscribe to state changes and notifications.

Events:
- ERROR: An error occurred within the SDK.
- AUTOPLAY_FAILED: Autoplay of media failed.
- KICKED_OUT: The current user was kicked out of the room.
- REMOTE_USER_ENTER: A remote user entered the room.
- REMOTE_USER_EXIT: A remote user exited the room.
- REMOTE_AUDIO_AVAILABLE: Remote audio track became available.
- REMOTE_AUDIO_UNAVAILABLE: Remote audio track became unavailable.
- REMOTE_VIDEO_AVAILABLE: Remote video track became available.
- REMOTE_VIDEO_UNAVAILABLE: Remote video track became unavailable.
- AUDIO_VOLUME: Audio volume level changed.
- AUDIO_FRAME: An audio frame was received.
- NETWORK_QUALITY: Network quality status changed.
- CONNECTION_STATE_CHANGED: The connection state of the SDK changed.
- AUDIO_PLAY_STATE_CHANGED: Audio playback state changed.
- VIDEO_PLAY_STATE_CHANGED: Video playback state changed.
- SCREEN_SHARE_STOPPED: Screen sharing session stopped.
- DEVICE_CHANGED: An audio or video device was changed.
- PUBLISH_STATE_CHANGED: The publishing state of local streams changed.
- TRACK: A media track event occurred.
- STATISTICS: SDK statistics were updated.
- SEI_MESSAGE: A Supplemental Enhancement Information (SEI) message was received.
- CUSTOM_MESSAGE: A custom message was received.
- FIRST_VIDEO_FRAME: The first video frame was rendered.
```

----------------------------------------

TITLE: TRTC Web SDK ERROR_CODE Module Constants
DESCRIPTION: Defines standard error codes returned by the TRTC Web SDK, indicating various failure conditions. These codes help developers diagnose issues such as invalid parameters, unsupported environments, device problems, or server errors, facilitating robust error handling and debugging.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-01-info-changelog

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Constants:
- INVALID_PARAMETER: Invalid parameter provided.
- INVALID_OPERATION: Invalid operation performed.
- ENV_NOT_SUPPORTED: Environment not supported.
- DEVICE_ERROR: Device error occurred.
- SERVER_ERROR: Server error occurred.
- OPERATION_FAILED: Operation failed.
- OPERATION_ABORT: Operation aborted.
- UNKNOWN_ERROR: Unknown error occurred.
```

----------------------------------------

TITLE: TRTC Web SDK Event Definitions (EVENT Module)
DESCRIPTION: Lists all events that can be emitted by the TRTC Web SDK, providing notifications for critical occurrences such as errors, autoplay failures, user kick-outs, remote user entry/exit, media availability changes, audio volume updates, network quality fluctuations, connection state changes, and various media playback states.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-02-info-webrtc-issues

LANGUAGE: APIDOC
CODE:
```
EVENT Module Constants:

ERROR: An error occurred within the SDK.
AUTOPLAY_FAILED: Indicates that media autoplay failed.
KICKED_OUT: The current user was kicked out of the room.
REMOTE_USER_ENTER: A remote user entered the room.
REMOTE_USER_EXIT: A remote user exited the room.
REMOTE_AUDIO_AVAILABLE: Remote audio became available for playback.
REMOTE_AUDIO_UNAVAILABLE: Remote audio became unavailable.
REMOTE_VIDEO_AVAILABLE: Remote video became available for playback.
REMOTE_VIDEO_UNAVAILABLE: Remote video became unavailable.
AUDIO_VOLUME: Reports changes in audio volume.
AUDIO_FRAME: Indicates an audio frame was received.
NETWORK_QUALITY: Reports changes in network quality.
CONNECTION_STATE_CHANGED: The connection state of the SDK changed.
AUDIO_PLAY_STATE_CHANGED: The audio playback state changed.
VIDEO_PLAY_STATE_CHANGED: The video playback state changed.
SCREEN_SHARE_STOPPED: Screen sharing has stopped.
DEVICE_CHANGED: An input/output device (e.g., camera, mic) was changed.
PUBLISH_STATE_CHANGED: The publishing state of local streams changed.
TRACK: A track-related event occurred.
STATISTICS: SDK statistics were updated.
SEI_MESSAGE: An SEI (Supplemental Enhancement Information) message was received.
CUSTOM_MESSAGE: A custom message was received.
FIRST_VIDEO_FRAME: The first video frame has been rendered.
```

----------------------------------------

TITLE: TRTC Web SDK ERROR_CODE Module Definitions
DESCRIPTION: Provides a comprehensive list of error codes and their descriptions, helping developers diagnose and handle issues encountered during TRTC Web SDK operations, such as invalid parameters, device errors, or server issues.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-12-basic-live-video

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Definitions:

INVALID_PARAMETER: An invalid parameter was provided to an SDK method.
INVALID_OPERATION: An invalid operation was attempted given the current SDK state.
ENV_NOT_SUPPORTED: The current environment or browser is not supported by the SDK.
DEVICE_ERROR: An error related to a media device (e.g., camera, microphone) occurred.
SERVER_ERROR: An error occurred on the TRTC server side.
OPERATION_FAILED: A requested operation failed to complete.
OPERATION_ABORT: A requested operation was aborted.
UNKNOWN_ERROR: An unknown or unclassified error occurred.
```

----------------------------------------

TITLE: TRTC SDK Error Object Properties and Handler
DESCRIPTION: Describes the static, readonly properties of an error object returned by the TRTC SDK, including `extraCode`, `functionName`, `message`, and the `handler` function for error recovery, particularly for media permission issues.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/RtcError

LANGUAGE: APIDOC
CODE:
```
TRTC SDK Error Object Properties:

(static, readonly) extraCode
  - Description: Extended error code.
  - See: Detailed error code list: ErrorCode

(static, readonly) functionName
  - Description: Name of the function that threw the error.

(static, readonly) message
  - Description: Error message.

(static, readonly) handler
  - Since: v5.2.0
  - Description: Error callback handler function, which can attempt to recover from certain errors.
  - Supported Errors:
    - extraCode 5302: When the system disables browser camera, microphone, or screen sharing permissions, `trtc.startLocalAudio`, `trtc.startLocalVideo`, `trtc.startScreenShare` will fail. Calling `error.handler()` can navigate to the system permission settings app, prompting users to enable permissions.
```

----------------------------------------

TITLE: TRTC Web SDK EVENT Module Constants
DESCRIPTION: Lists various events that can be emitted by the TRTC Web SDK, providing notifications about changes in connection state, device status, user presence, audio/video availability, and other operational occurrences.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-41-advanced-small-stream-auto-switcher

LANGUAGE: APIDOC
CODE:
```
EVENT Module Constants:

- ERROR: Emitted when an SDK error occurs.
- AUTOPLAY_FAILED: Emitted when browser autoplay is blocked.
- KICKED_OUT: Emitted when the user is kicked out of the room.
- REMOTE_USER_ENTER: Emitted when a remote user enters the room.
- REMOTE_USER_EXIT: Emitted when a remote user exits the room.
- REMOTE_AUDIO_AVAILABLE: Emitted when a remote user's audio becomes available.
- REMOTE_AUDIO_UNAVAILABLE: Emitted when a remote user's audio becomes unavailable.
- REMOTE_VIDEO_AVAILABLE: Emitted when a remote user's video becomes available.
- REMOTE_VIDEO_UNAVAILABLE: Emitted when a remote user's video becomes unavailable.
- AUDIO_VOLUME: Emitted periodically with current audio volume levels.
- AUDIO_FRAME: Emitted when an audio frame is received (for custom processing).
- NETWORK_QUALITY: Emitted periodically with network quality statistics.
- CONNECTION_STATE_CHANGED: Emitted when the connection state changes.
- AUDIO_PLAY_STATE_CHANGED: Emitted when the audio playback state changes.
- VIDEO_PLAY_STATE_CHANGED: Emitted when the video playback state changes.
- SCREEN_SHARE_STOPPED: Emitted when screen sharing stops.
- DEVICE_CHANGED: Emitted when an input/output device changes.
- PUBLISH_STATE_CHANGED: Emitted when the publishing state changes.
- TRACK: Emitted for track-related events.
- STATISTICS: Emitted periodically with SDK statistics.
- SEI_MESSAGE: Emitted when an SEI message is received.
- CUSTOM_MESSAGE: Emitted when a custom message is received.
- FIRST_VIDEO_FRAME: Emitted when the first video frame is rendered.
```

----------------------------------------

TITLE: TRTC Web SDK EVENT Module Constants
DESCRIPTION: Lists all events dispatched by the TRTC Web SDK, covering connection states, user presence, audio/video availability, device changes, and various playback states. Developers can subscribe to these events to react to changes in the SDK's status and user interactions.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-24-advanced-network-quality

LANGUAGE: APIDOC
CODE:
```
EVENT Module:
  ERROR: An error occurred.
  AUTOPLAY_FAILED: Autoplay failed.
  KICKED_OUT: User was kicked out.
  REMOTE_USER_ENTER: A remote user entered the room.
  REMOTE_USER_EXIT: A remote user exited the room.
  REMOTE_AUDIO_AVAILABLE: Remote audio became available.
  REMOTE_AUDIO_UNAVAILABLE: Remote audio became unavailable.
  REMOTE_VIDEO_AVAILABLE: Remote video became available.
  REMOTE_VIDEO_UNAVAILABLE: Remote video became unavailable.
  AUDIO_VOLUME: Audio volume changed.
  AUDIO_FRAME: Audio frame received.
  NETWORK_QUALITY: Network quality changed.
  CONNECTION_STATE_CHANGED: Connection state changed.
  AUDIO_PLAY_STATE_CHANGED: Audio playback state changed.
  VIDEO_PLAY_STATE_CHANGED: Video playback state changed.
  SCREEN_SHARE_STOPPED: Screen sharing stopped.
  DEVICE_CHANGED: Device changed.
  PUBLISH_STATE_CHANGED: Publish state changed.
  TRACK: Track event.
  STATISTICS: Statistics updated.
  SEI_MESSAGE: SEI message received.
  CUSTOM_MESSAGE: Custom message received.
  FIRST_VIDEO_FRAME: First video frame rendered.
```

----------------------------------------

TITLE: Remove macOS Virtual Camera Driver (Chrome Workaround)
DESCRIPTION: This command provides a workaround for a known issue where Chrome fails to fetch the camera list on macOS devices due to the Mersive Solstic virtual camera driver. Executing this command with superuser privileges removes the problematic `RelayCam.plugin` file from the system's CoreMediaIO plugins directory. This action aims to resolve camera detection issues in Chrome caused by the virtual driver.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-02-info-webrtc-issues

LANGUAGE: js
CODE:
```
sudo rm -rf /Library/CoreMediaIO/Plug-Ins/DAL/RelayCam.plugin
```

----------------------------------------

TITLE: TRTC Web SDK EVENT Module Constants
DESCRIPTION: Lists all events dispatched by the TRTC Web SDK, providing notifications for various occurrences such as errors, autoplay failures, user presence changes, audio/video availability, network quality, connection state, and device changes.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-41-advanced-small-stream-auto-switcher

LANGUAGE: APIDOC
CODE:
```
EVENT Module Constants:

ERROR: An error occurred.
AUTOPLAY_FAILED: Autoplay failed (e.g., browser policy).
KICKED_OUT: User was kicked out of the room.
REMOTE_USER_ENTER: A remote user entered the room.
REMOTE_USER_EXIT: A remote user exited the room.
REMOTE_AUDIO_AVAILABLE: Remote audio track became available.
REMOTE_AUDIO_UNAVAILABLE: Remote audio track became unavailable.
REMOTE_VIDEO_AVAILABLE: Remote video track became available.
REMOTE_VIDEO_UNAVAILABLE: Remote video track became unavailable.
AUDIO_VOLUME: Audio volume changed.
AUDIO_FRAME: Audio frame data available.
NETWORK_QUALITY: Network quality changed.
CONNECTION_STATE_CHANGED: Connection state changed.
AUDIO_PLAY_STATE_CHANGED: Audio playback state changed.
VIDEO_PLAY_STATE_CHANGED: Video playback state changed.
SCREEN_SHARE_STOPPED: Screen sharing stopped.
DEVICE_CHANGED: Audio/video device changed.
PUBLISH_STATE_CHANGED: Publish state changed.
TRACK: Track related event.
STATISTICS: Statistics data available.
SEI_MESSAGE: SEI (Supplemental Enhancement Information) message received.
CUSTOM_MESSAGE: Custom message received.
FIRST_VIDEO_FRAME: First video frame rendered.
```

----------------------------------------

TITLE: TRTC SDK Event Types (EVENT)
DESCRIPTION: Lists various events dispatched by the TRTC SDK, indicating changes in connection state, user presence, media availability, device status, and more. Applications can listen to these events to react to real-time changes.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-27-advanced-small-stream

LANGUAGE: APIDOC
CODE:
```
EVENT Module Events:
  ERROR: General error event.
  AUTOPLAY_FAILED: Autoplay failure event.
  KICKED_OUT: User kicked out event.
  REMOTE_USER_ENTER: Remote user enters room.
  REMOTE_USER_EXIT: Remote user exits room.
  REMOTE_AUDIO_AVAILABLE: Remote audio stream becomes available.
  REMOTE_AUDIO_UNAVAILABLE: Remote audio stream becomes unavailable.
  REMOTE_VIDEO_AVAILABLE: Remote video stream becomes available.
  REMOTE_VIDEO_UNAVAILABLE: Remote video stream becomes unavailable.
  AUDIO_VOLUME: Audio volume change event.
  AUDIO_FRAME: Audio frame event.
  NETWORK_QUALITY: Network quality change event.
  CONNECTION_STATE_CHANGED: Connection state changed event.
  AUDIO_PLAY_STATE_CHANGED: Audio play state changed event.
  VIDEO_PLAY_STATE_CHANGED: Video play state changed event.
  SCREEN_SHARE_STOPPED: Screen sharing stopped event.
  DEVICE_CHANGED: Device changed event.
  PUBLISH_STATE_CHANGED: Publish state changed event.
  TRACK: Track event.
  STATISTICS: Statistics event.
  SEI_MESSAGE: SEI message received event.
  CUSTOM_MESSAGE: Custom message received event.
  FIRST_VIDEO_FRAME: First video frame rendered event.
```

----------------------------------------

TITLE: RtcError Class API Reference
DESCRIPTION: Documents the RtcError class, providing properties to access detailed information about errors encountered within the TRTC Web SDK. This class helps in debugging and handling specific error conditions.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-23-advanced-support-detection

LANGUAGE: APIDOC
CODE:
```
RtcError Class Properties:
  code: The primary error code.
  extraCode: Additional error code details.
  functionName: The name of the function where the error occurred.
  message: A descriptive error message.
  handler: The error handler associated with the error.
```

----------------------------------------

TITLE: RtcError Class: Error Properties
DESCRIPTION: This section describes the properties of the RtcError class, which provides detailed information about errors encountered during TRTC operations. These properties help in diagnosing issues by providing error codes, messages, and context.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-00-info-update-guideline

LANGUAGE: APIDOC
CODE:
```
RtcError.code
RtcError.extraCode
RtcError.functionName
RtcError.message
RtcError.handler
```

----------------------------------------

TITLE: Handling Local Video and Audio Acquisition Exceptions in TRTC Web SDK
DESCRIPTION: This code listens for `TRTC.EVENT.VIDEO_PLAY_STATE_CHANGED` and `TRTC.EVENT.AUDIO_PLAY_STATE_CHANGED` events to detect issues with local camera and microphone acquisition. It identifies scenarios where the local stream is muted or ended, indicating a potential acquisition problem, and suggests guiding the user to check their devices as the SDK attempts automatic recovery.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-25-advanced-device-change

LANGUAGE: javascript
CODE:
```
trtc.on(TRTC.EVENT.VIDEO_PLAY_STATE_CHANGED, event => {
  // 本地摄像头采集异常，此时 SDK 会尝试自动恢复采集，您可以引导用户检查摄像头是否正常。
  if (event.userId === '' && event.streamType === TRTC.TYPE.STREAM_TYPE_MAIN && (event.reason === 'mute' || event.reason === 'ended')) {}
});
trtc.on(TRTC.EVENT.AUDIO_PLAY_STATE_CHANGED, event => {
  // 本地麦克风采集异常，此时 SDK 会尝试自动恢复采集，您可以引导用户检查麦克风是否正常。
  if (event.userId === '' && (event.reason === 'mute' || event.reason === 'ended')) {}
});
```

----------------------------------------

TITLE: TRTC Web SDK Event Module Definitions
DESCRIPTION: Lists all events dispatched by the TRTC Web SDK, covering connection states, user presence, media availability, device changes, and various playback and publishing states, allowing applications to react to SDK activities.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-30-advanced-cross-room-link

LANGUAGE: APIDOC
CODE:
```
EVENT Module Events:

ERROR: An error occurred.
AUTOPLAY_FAILED: Autoplay of media failed.
KICKED_OUT: User was kicked out of the room.
REMOTE_USER_ENTER: A remote user entered the room.
REMOTE_USER_EXIT: A remote user exited the room.
REMOTE_AUDIO_AVAILABLE: Remote audio track became available.
REMOTE_AUDIO_UNAVAILABLE: Remote audio track became unavailable.
REMOTE_VIDEO_AVAILABLE: Remote video track became available.
REMOTE_VIDEO_UNAVAILABLE: Remote video track became unavailable.
AUDIO_VOLUME: Audio volume changed.
AUDIO_FRAME: Audio frame received.
NETWORK_QUALITY: Network quality changed.
CONNECTION_STATE_CHANGED: Connection state changed.
AUDIO_PLAY_STATE_CHANGED: Audio playback state changed.
VIDEO_PLAY_STATE_CHANGED: Video playback state changed.
SCREEN_SHARE_STOPPED: Screen sharing stopped.
DEVICE_CHANGED: Media device (camera, mic, speaker) changed.
PUBLISH_STATE_CHANGED: Publishing state changed.
TRACK: Track related event.
STATISTICS: Statistics updated.
SEI_MESSAGE: SEI (Supplemental Enhancement Information) message received.
CUSTOM_MESSAGE: Custom message received.
FIRST_VIDEO_FRAME: First video frame rendered.
```

----------------------------------------

TITLE: RtcError Class API Reference
DESCRIPTION: API documentation for the RtcError class, which represents errors encountered within the TRTC Web SDK. It provides detailed properties to help identify and diagnose issues during real-time communication.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/RtcError

LANGUAGE: APIDOC
CODE:
```
RtcError Class Properties:

  code: number
    - Description: The primary error code indicating the type of error.
    - Type: Number.

  extraCode: number
    - Description: An additional error code providing more specific details about the error.
    - Type: Number.

  functionName: string
    - Description: The name of the TRTC SDK function or method where the error occurred.
    - Type: String.

  message: string
    - Description: A human-readable error message describing the issue.
    - Type: String.

  handler: Function | null
    - Description: A reference to the handler function that was executing when the error occurred, if applicable.
    - Type: Function or null.
```

----------------------------------------

TITLE: TRTC Web SDK Real-time Statistics Structures
DESCRIPTION: Defines the data structures for real-time statistics provided by the TRTC SDK, covering overall connection metrics, local audio/video statistics, and remote user audio/video statistics. These structures provide insights into network quality and media performance.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/global

LANGUAGE: APIDOC
CODE:
```
TRTCStatistics:
  Properties:
    rtt: number - The round-trip time from SDK to TRTC server(SDK -> TRTC server -> SDK). Unit: ms.
    upLoss: number - Uplink loss rate from SDK to TRTC server. Unit: %
    downLoss: number - Downlink loss rate from TRTC server to SDK. Unit: %
    bytesSent: number - Total bytes sent, including signaling data and media data. Unit: bytes.
    bytesReceived: number - Total bytes received, including signaling data and media data. Unit: bytes.
    localStatistics: TRTCLocalStatistics - Local statistics.
    remoteStatistics: Array.<TRTCRemoteStatistics> - Remote statistics.

TRTCLocalStatistics:
  Properties:
    audio: TRTCAudioStatistic - Local audio statistics
    video: Array.<TRTCVideoStatistic> - Local video statistics
  Description: Local statistics

TRTCRemoteStatistics:
  Properties:
    userId: string - The userId of remote user
    audio: TRTCAudioStatistic - Remote audio statistics
    video: Array.<TRTCVideoStatistic> - Remote video statistics
  Description: Remote statistics.

TRTCAudioStatistic:
  Properties:
    bitrate: number - Audio bitrate. Unit: kbps
    audioLevel: number - Audio level. Value: float from 0 to 1.
    jitterBufferDelay: number - Playback delay, unit: ms. Since `v5.11.0`
    point2pointDelay: number - End-to-end delay, unit: ms. This indicator is an estimate and may be affected by network quality. Since `v5.11.0`
  Description: Audio statistics

TRTCVideoStatistic:
  Properties:
    bitrate: number - Video bitrate. Unit: kbps
    width: number - Video width
    height: number - Video height
    frameRate: number - Video frameRate
    videoType: 'big' | 'small' | 'sub' - Video type: big, small, sub.
    jitterBufferDelay: number - Playback delay, unit: ms. Since `v5.11.0`
    point2pointDelay: number - End-to-end delay, unit: ms. This indicator is an estimate and may be affected by network quality. Since `v5.11.0`
  Description: Video statistics
```

----------------------------------------

TITLE: Retrieve Network Quality Statistics in TRTC Web SDK
DESCRIPTION: The `NETWORK_QUALITY` event provides statistics on local uplink and downlink network conditions, triggered every two seconds after entering the room. It includes RTT, packet loss, and a quality rating.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/module-EVENT

LANGUAGE: APIDOC
CODE:
```
TRTC.EVENT.NETWORK_QUALITY
  - Default Value: 'network-quality'
  - Description: Network quality statistics data event, which starts to be counted after entering the room and triggers every two seconds. This data reflects the network quality of your local uplink and downlink.
  - Notes:
    - The uplink network quality (uplinkNetworkQuality) refers to the network situation of uploading local streams (uplink connection network quality from SDK to Tencent Cloud).
    - The downlink network quality (downlinkNetworkQuality) refers to the average network situation of downloading all streams (average network quality of all downlink connections from Tencent Cloud to SDK).
    - If you want to know the uplink and downlink network conditions of the other party, you need to broadcast the other party's network quality through IM.
  - Event Object Properties:
    - uplinkNetworkQuality: number - Uplink network quality.
    - downlinkNetworkQuality: number - Downlink network quality.
    - uplinkRTT: number - Uplink RTT in ms.
    - uplinkLoss: number - Uplink packet loss rate.
    - downlinkRTT: number - Average downlink RTT in ms.
    - downlinkLoss: number - Average downlink packet loss rate.
  - Network Quality Values:
    | Value | Meaning                                                              |
    | ----- | -------------------------------------------------------------------- |
    | 0     | Network state is unknown (no uplink/downlink connection established) |
    | 1     | Network state is excellent                                           |
    | 2     | Network state is good                                                |
    | 3     | Network state is average                                             |
    | 4     | Network state is poor                                                |
    | 5     | Network state is very poor                                           |
    | 6     | Network connection is disconnected                                   |
```

----------------------------------------

TITLE: RtcError Class Properties Reference
DESCRIPTION: This section outlines the properties of the RtcError class, which provides detailed information about errors encountered during TRTC SDK operations. It helps in diagnosing issues by providing error codes, messages, and context.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-00-info-update-guideline

LANGUAGE: APIDOC
CODE:
```
RtcError Class:
  - code: Property representing the error code.
  - extraCode: Property representing an extra error code.
  - functionName: Property representing the name of the function where the error occurred.
  - message: Property representing the error message.
  - handler: Property representing the error handler.
```

----------------------------------------

TITLE: TRTC Web SDK ERROR_CODE Module Constants
DESCRIPTION: Defines various error codes that can be returned by the TRTC Web SDK, indicating specific issues such as invalid parameters, unsupported environments, device problems, or server-side errors.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-41-advanced-small-stream-auto-switcher

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Constants:

- INVALID_PARAMETER: Indicates an invalid parameter was provided to an SDK method.
- INVALID_OPERATION: Indicates an operation was performed in an invalid state.
- ENV_NOT_SUPPORTED: Indicates the current environment is not supported by the SDK.
- DEVICE_ERROR: Indicates an error related to an audio/video device.
- SERVER_ERROR: Indicates an error originating from the TRTC server.
- OPERATION_FAILED: Indicates a general operation failure.
- OPERATION_ABORT: Indicates an operation was aborted.
- UNKNOWN_ERROR: Indicates an unknown or unclassified error.
```

----------------------------------------

TITLE: TRTC.EVENT.NETWORK_QUALITY Event Reference
DESCRIPTION: The NETWORK_QUALITY event provides real-time updates on the network conditions experienced by the TRTC client. It includes comprehensive metrics for both uplink and downlink, such as network quality scores, Round-Trip Time (RTT), and packet loss rates, enabling applications to react to changing network environments.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-24-advanced-network-quality

LANGUAGE: APIDOC
CODE:
```
TRTC.EVENT.NETWORK_QUALITY event
  - Description: Event emitted to report real-time network quality metrics.
  - Event Object Properties:
    - uplinkNetworkQuality: Number (e.g., 1=excellent, 6=disconnected) - Quality score for uplink.
    - downlinkNetworkQuality: Number (e.g., 1=excellent, 6=disconnected) - Quality score for downlink.
    - uplinkRTT: Number (ms) - Round-Trip Time for uplink.
    - uplinkLoss: Number (%) - Packet loss rate for uplink.
    - downlinkRTT: Number (ms) - Round-Trip Time for downlink.
    - downlinkLoss: Number (%) - Packet loss rate for downlink.
```

----------------------------------------

TITLE: TRTC Web SDK Error Codes
DESCRIPTION: Defines common error codes returned by the TRTC Web SDK, indicating various issues such as invalid parameters, device errors, server problems, or operational failures. These codes help in debugging and handling exceptional conditions.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-28-advanced-beauty

LANGUAGE: APIDOC
CODE:
```
Module: ERROR_CODE
  INVALID_PARAMETER: Invalid parameter provided.
  INVALID_OPERATION: Invalid operation performed.
  ENV_NOT_SUPPORTED: Environment not supported.
  DEVICE_ERROR: Device error occurred.
  SERVER_ERROR: Server error occurred.
  OPERATION_FAILED: Operation failed.
  OPERATION_ABORT: Operation aborted.
  UNKNOWN_ERROR: Unknown error occurred.
```

----------------------------------------

TITLE: RtcError Class Properties
DESCRIPTION: Documentation for the RtcError class, detailing its properties for identifying and handling real-time communication errors.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-30-advanced-cross-room-link

LANGUAGE: APIDOC
CODE:
```
RtcError Class:
  code: number
    - The primary error code indicating the type of error.
  extraCode: number
    - An additional error code providing more specific details.
  functionName: string
    - The name of the SDK function or method where the error originated.
  message: string
    - A human-readable description of the error.
  handler: any
    - Reference to the error handler or context.
```

----------------------------------------

TITLE: API Reference for TRTC Web SDK Events
DESCRIPTION: Details the various events dispatched by the TRTC Web SDK, indicating changes in connection state, user presence, media availability, and other operational statuses. Applications can subscribe to these events to react to real-time communication lifecycle changes.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-17-basic-detect-volume

LANGUAGE: APIDOC
CODE:
```
EVENT Module Events:

ERROR: An error occurred.
AUTOPLAY_FAILED: Autoplay of media failed.
KICKED_OUT: User was kicked out of the room.
REMOTE_USER_ENTER: A remote user entered the room.
REMOTE_USER_EXIT: A remote user exited the room.
REMOTE_AUDIO_AVAILABLE: Remote audio stream became available.
REMOTE_AUDIO_UNAVAILABLE: Remote audio stream became unavailable.
REMOTE_VIDEO_AVAILABLE: Remote video stream became available.
REMOTE_VIDEO_UNAVAILABLE: Remote video stream became unavailable.
AUDIO_VOLUME: Audio volume changed.
AUDIO_FRAME: Audio frame data available.
NETWORK_QUALITY: Network quality changed.
CONNECTION_STATE_CHANGED: Connection state changed.
AUDIO_PLAY_STATE_CHANGED: Audio playback state changed.
VIDEO_PLAY_STATE_CHANGED: Video playback state changed.
SCREEN_SHARE_STOPPED: Screen sharing stopped.
DEVICE_CHANGED: Media device (camera, mic) changed.
PUBLISH_STATE_CHANGED: Publish state changed.
TRACK: Track related event.
STATISTICS: Statistics data available.
SEI_MESSAGE: SEI (Supplemental Enhancement Information) message received.
CUSTOM_MESSAGE: Custom message received.
FIRST_VIDEO_FRAME: First video frame rendered.
```

----------------------------------------

TITLE: WebRTC SDK OPERATION_FAILED Error (5500)
DESCRIPTION: This entry documents the `OPERATION_FAILED` error, which signifies an exception the SDK cannot resolve after multiple retries, even when API call requirements are met. It typically points to browser or network issues. The documentation includes its default value, a detailed description, interfaces that may throw this error, handling suggestions, and specific sub-error codes with their explanations.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/module-ERROR_CODE

LANGUAGE: APIDOC
CODE:
```
#### (static) OPERATION\_FAILED

Default Value:
:   * 5500

Description: The exception that the SDK cannot solve after multiple retries under the condition of meeting the API call requirements, usually caused by browser or network problems.
The following interfaces will throw this error code when an exception occurs: `enterRoom`, `startLocalVideo`, `startLocalAudio`, `startScreenShare`, `startRemoteVideo`, `switchRole`
Handling suggestions:

* Confirm whether the domain name and port required for communication meet your network environment requirements, refer to the document [Handle Firewall Restriction](tutorial-34-advanced-proxy.html)
* Other issues need to be handled by engineers. [Contact us on telegram](https://t.me/%2BEPk6TMZEZMM5OGY1)

| extraCode | Description |
| --- | --- |
| 5501 | Firewall restriction: After multiple retries, the SDK still cannot establish a media connection, which will cause streaming and pulling to fail. |
| 5502 | Re-entering the room failed: When the user experiences a network outage of more than 30s, the SDK will try to re-enter the room to restore the call, but the re-entry may fail due to the expiration of userSig, and this error will be thrown. |
| 5503 | Re-entering the room failed: When the user experiences a network outage of more than 30s, the SDK will try to re-enter the room to restore the call, but the re-entry may fail due to the expiration of userSig, and this error will be thrown. |
```

----------------------------------------

TITLE: RtcError Class API Reference
DESCRIPTION: API documentation for the RtcError class, detailing its properties for error handling and debugging within the TRTC Web SDK.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-35-advanced-ai-denoiser

LANGUAGE: APIDOC
CODE:
```
RtcError Class Properties:

  RtcError.code
    - The error code.
  RtcError.extraCode
    - An extra error code for more specific details.
  RtcError.functionName
    - The name of the function where the error occurred.
  RtcError.message
    - A descriptive error message.
  RtcError.handler
    - The error handler.
```

----------------------------------------

TITLE: Initialize TRTC SDK and Start Cross-Room Connection
DESCRIPTION: This JavaScript snippet demonstrates how to integrate the CrossRoom plugin into the TRTC SDK, enter a room, and then initiate a cross-room connection. It illustrates connecting to a target room either at a room level (all anchors) or user level (specific anchor).

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-30-advanced-cross-room-link

LANGUAGE: JavaScript
CODE:
```
import { CrossRoom } from 'trtc-sdk-v5/plugins/cross-room';
const trtc = TRTC.create({ plugins: [CrossRoom] });
await trtc.enterRoom({ sdkAppId, userId: 'user1', userSig, roomId: 7777 });
// Connect user1 in room 7777 with user2 in room 8888. The stream of user2 will be pushed to room 7777, and the stream of user1 will be pushed to room 8888.
await trtc.startPlugin('CrossRoom', {
  roomId: 8888,
  // Choose either roomId or strRoomId
  // strRoomId: '8888'
  userId: 'user2' // If not provided, it indicates a room-level cross-room connection
});
```

----------------------------------------

TITLE: Detect Network Quality During TRTC Call
DESCRIPTION: This JavaScript snippet demonstrates how to monitor network quality in real-time during an active TRTC call. It subscribes to the TRTC.EVENT.NETWORK_QUALITY event and logs detailed metrics such as uplink/downlink quality, Round-Trip Time (RTT), and packet loss.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-24-advanced-network-quality

LANGUAGE: JavaScript
CODE:
```
const trtc = TRTC.create();
trtc.on(TRTC.EVENT.NETWORK_QUALITY, event => {
   console.log(`network-quality, uplinkNetworkQuality:${event.uplinkNetworkQuality}, downlinkNetworkQuality: ${event.downlinkNetworkQuality}`)
   console.log(`uplink rtt:${event.uplinkRTT} loss:${event.uplinkLoss}`)
   console.log(`downlink rtt:${event.downlinkRTT} loss:${event.downlinkLoss}`)
})
```

----------------------------------------

TITLE: TRTC Web SDK Network Quality Enumeration and Bandwidth Management APIs
DESCRIPTION: This section defines the enumeration values for network quality reported by the TRTC Web SDK, ranging from unknown to extremely poor, and provides guidance on interpreting these values. It also outlines recommended TRTC API methods for managing bandwidth consumption based on detected network conditions, specifically for reducing uplink usage.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-24-advanced-network-quality

LANGUAGE: APIDOC
CODE:
```
TRTC Network Quality Enumeration:
  Value | Meaning
  --- | ---
  0     | The network condition is unknown, indicating that the current TRTC instance has not established an uplink/downlink connection
  1     | The network condition is excellent
  2     | The network condition is good
  3     | The network condition is average
  4     | The network condition is poor
  5     | The network condition is extremely poor
  6     | The network connection has been disconnected. Note: If the downlink network quality is this value, it means that all downlink connections have been disconnected.

TRTC API Methods for Bandwidth Management:

TRTC.updateLocalVideo(params)
  - Description: Adjusts local video parameters (e.g., bitrate) to reduce uplink bandwidth consumption.
  - Usage Context: Recommended when uplink network quality is greater than 3.
  - Related Link: [TRTC.html#updateLocalVideo]

TRTC.stopLocalVideo()
  - Description: Stops local video transmission entirely to reduce uplink bandwidth consumption.
  - Usage Context: Recommended when uplink network quality is greater than 3.
  - Related Link: [TRTC.html#stopLocalVideo]
```

----------------------------------------

TITLE: TRTC WebRTC SDK Event Definitions
DESCRIPTION: Lists all events dispatched by the TRTC WebRTC SDK, covering critical aspects such as connection state changes, remote user entry/exit, availability of remote audio/video streams, media playback states, device changes, network quality updates, and custom message handling.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-04-info-uplink-limits

LANGUAGE: APIDOC
CODE:
```
Module: EVENT
Events:
  ERROR: An error occurred within the SDK.
  AUTOPLAY_FAILED: Autoplay of media failed, often due to browser policies.
  KICKED_OUT: The current user was kicked out of the room.
  REMOTE_USER_ENTER: A remote user entered the room.
  REMOTE_USER_EXIT: A remote user exited the room.
  REMOTE_AUDIO_AVAILABLE: A remote user's audio stream became available.
  REMOTE_AUDIO_UNAVAILABLE: A remote user's audio stream became unavailable.
  REMOTE_VIDEO_AVAILABLE: A remote user's video stream became available.
  REMOTE_VIDEO_UNAVAILABLE: A remote user's video stream became unavailable.
  AUDIO_VOLUME: Reports the current audio volume levels.
  AUDIO_FRAME: Indicates an audio frame has been processed or received.
  NETWORK_QUALITY: Reports changes in network quality.
  CONNECTION_STATE_CHANGED: The SDK's connection state to the server changed.
  AUDIO_PLAY_STATE_CHANGED: The audio playback state changed (e.g., playing, paused).
  VIDEO_PLAY_STATE_CHANGED: The video playback state changed (e.g., playing, paused).
  SCREEN_SHARE_STOPPED: Screen sharing session has stopped.
  DEVICE_CHANGED: An input/output device (e.g., camera, microphone) has changed.
  PUBLISH_STATE_CHANGED: The publishing state of local streams changed.
  TRACK: Generic event related to media tracks.
  STATISTICS: Provides updated performance statistics.
  SEI_MESSAGE: Supplemental Enhancement Information (SEI) message received.
  CUSTOM_MESSAGE: A custom message was received.
  FIRST_VIDEO_FRAME: The first video frame from a remote stream has been rendered.
```

----------------------------------------

TITLE: TRTC Web SDK Event Module Definitions
DESCRIPTION: Lists all events that can be emitted by the TRTC Web SDK, covering a wide range of scenarios such as errors, user lifecycle (enter/exit), stream availability (audio/video), network quality changes, device changes, connection state, and media playback states. Developers can subscribe to these events to manage application logic and user interface updates.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-15-basic-dynamic-add-video

LANGUAGE: APIDOC
CODE:
```
EVENT Module Definitions:

ERROR: An error occurred.
AUTOPLAY_FAILED: Autoplay failed.
KICKED_OUT: User was kicked out.
REMOTE_USER_ENTER: A remote user entered the room.
REMOTE_USER_EXIT: A remote user exited the room.
REMOTE_AUDIO_AVAILABLE: Remote audio track became available.
REMOTE_AUDIO_UNAVAILABLE: Remote audio track became unavailable.
REMOTE_VIDEO_AVAILABLE: Remote video track became available.
REMOTE_VIDEO_UNAVAILABLE: Remote video track became unavailable.
AUDIO_VOLUME: Audio volume changed.
AUDIO_FRAME: Audio frame received.
NETWORK_QUALITY: Network quality changed.
CONNECTION_STATE_CHANGED: Connection state changed.
AUDIO_PLAY_STATE_CHANGED: Audio playback state changed.
VIDEO_PLAY_STATE_CHANGED: Video playback state changed.
SCREEN_SHARE_STOPPED: Screen sharing stopped.
DEVICE_CHANGED: Device (e.g., camera, microphone) changed.
PUBLISH_STATE_CHANGED: Publish state changed.
TRACK: Track related event.
STATISTICS: Statistics updated.
SEI_MESSAGE: SEI message received.
CUSTOM_MESSAGE: Custom message received.
FIRST_VIDEO_FRAME: First video frame rendered.
```

----------------------------------------

TITLE: TRTC Web SDK Error Code Definitions (ERROR_CODE Module)
DESCRIPTION: Defines common error codes returned by the TRTC Web SDK, indicating various issues such as invalid parameters provided to SDK methods, invalid operations, unsupported environments, device-related problems, server-side errors, or general operation failures and abortions.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-02-info-webrtc-issues

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Constants:

INVALID_PARAMETER: An invalid parameter was provided to an SDK method.
INVALID_OPERATION: An operation was attempted that is not valid in the current state.
ENV_NOT_SUPPORTED: The current environment or browser is not supported by the SDK.
DEVICE_ERROR: An error occurred with a media device (e.g., camera, microphone).
SERVER_ERROR: An error originated from the TRTC server.
OPERATION_FAILED: A general operation failed to complete.
OPERATION_ABORT: An operation was aborted.
UNKNOWN_ERROR: An unknown or unclassified error occurred.
```

----------------------------------------

TITLE: QCloud TRTC Web SDK Error Code Definitions
DESCRIPTION: Defines standard error codes returned by the QCloud TRTC Web SDK, indicating various issues such as invalid parameters, device errors, or server problems. These codes help in debugging and handling exceptional conditions gracefully.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-29-advanced-water-mark

LANGUAGE: APIDOC
CODE:
```
Module: ERROR_CODE
  INVALID_PARAMETER: An invalid parameter was provided to an SDK method.
  INVALID_OPERATION: An operation was attempted that is not valid in the current state.
  ENV_NOT_SUPPORTED: The current environment (browser, OS) is not supported.
  DEVICE_ERROR: An error occurred with a media device (e.g., camera, microphone).
  SERVER_ERROR: An error occurred on the TRTC server side.
  OPERATION_FAILED: A general operation failed to complete.
  OPERATION_ABORT: An operation was aborted.
  UNKNOWN_ERROR: An unknown or unclassified error occurred.
```

----------------------------------------

TITLE: TRTC Web SDK SERVER_ERROR Codes Reference
DESCRIPTION: Comprehensive documentation for the static `SERVER_ERROR` constant in the TRTC Web SDK. This section details various server-side error codes (`extraCode`) that can be thrown by core methods like `enterRoom`, `startLocalVideo`, `startLocalAudio`, `startScreenShare`, `startRemoteVideo`, and `switchRole`. It includes default values, descriptions, affected APIs, general handling advice, and specific details for each `extraCode`.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/module-ERROR_CODE

LANGUAGE: APIDOC
CODE:
```
SERVER_ERROR (static)
  Default Value: 5400
  Description: Thrown when abnormal data is received from the server.
  Affected APIs: enterRoom, startLocalVideo, startLocalAudio, startScreenShare, startRemoteVideo, switchRole
  Handling Advice: Server-side exceptions are typically handled during development. Common issues include expired userSig, Tencent Cloud account arrears, or unactivated TRTC service.

  extraCode Details:
    -8: sdkAppId is incorrect, please check if sdkAppId is correctly filled.
    -10012: roomId not provided or does not meet specifications. If using string roomId, use strRoomId when calling trtc.enterRoom.
    -10015: Server failed to get server node.
    -10016: Server internal communication timeout (3s).
    -10035: Server failed to switch room.
    -10037: Anchor role does not support room switching.
    -100006: Permission check failed. If advanced permission control is enabled, check the privateMapKey parameter carried in trtc.enterRoom. See "Enable Advanced Permission Settings".
    -100013: Customer service arrears. Log in to TRTC console, click your application, then "Account Info" to confirm service status.
    -100021: Server overloaded, failed to enter room.
    -100022: Server allocation failed.
    -100024: TRTC service not activated, leading to failed room entry. Activate TRTC service for your application in the IM console.
    -102006: Flow control defined error code (add user failed).
    -102010: With advanced permission control enabled, user does not have permission to create a room. See "Enable Advanced Permission Settings".
    -102023: Request parameter error (request parameter error generated by backend interface service).
    70001: userSig expired. Please try regenerating. If it expires immediately after generation, check if the validity period is too small or mistakenly set to 0.
    70002: userSig length is 0. Please confirm if signature calculation is correct. Access sign_src for simple source code to calculate signature, verify parameters, and ensure signature correctness.
    70003, 70004: userSig validation failed. Please confirm if userSig content is truncated, e.g., due to insufficient buffer length.
    70005, 70006, 70007, 70008, 70010: userSig validation failed. Verify generated userSig with a tool.
    70009: userSig validation failed with business public key. Please confirm if the private key used to generate userSig corresponds to the sdkAppId.
    70013: userId in userSig does not match userId in request. Check if userId entered during login matches the one in userSig.
    70014: sdkAppId in userSig does not match sdkAppId in request. Check if sdkAppId entered during login matches the one in userSig.
    70015: No validation method found for this sdkAppId and account type. Please confirm if account integration has been performed.
    70016: Pulled public key length is 0. Please confirm if public key has been uploaded. If it's a re-uploaded public key, try again after ten minutes.
    70017: Internal third-party ticket validation timeout. Please retry. If multiple retries still fail, contact TLS account support.
    70018: Internal third-party ticket validation failed.
    70019: HTTPS ticket field is empty. Please fill userSig correctly.
    70020: sdkAppId not found. Please confirm if it has been configured on Tencent Cloud.
    70052: userSig has expired. Please regenerate and try again.
    70101: Request package information is empty.
    70102: Request package account type error.
    70103: Phone number format error.
    70104: Email format error.
    70105: TLS account format error.
    70106: Illegal account format type.
    70107: userId not registered.
    70113: Batch quantity illegal.
    70114: Restricted for security reasons.
    70115: uin is not the developer uin for the corresponding sdkAppId.
    70140: sdkAppId and acctype mismatch.
    70145: Account type error.
    70169, 70201, 70202, 70203: Internal error. Please retry. If multiple retries still fail, contact TLS account support.
    70204: sdkAppId has no corresponding acctype.
    70205: Failed to find acctype. Please retry.
    70206: Illegal batch quantity in request.
    70207, 70208: Internal error. Please retry.
    70209: Failed to get developer uin flag.
    70210: uin in request is not developer uin.
    70211: uin in request is illegal.
    70212, 70213: Internal error. Please retry. If multiple retries still fail, contact TLS account support.
    70214: Internal ticket validation failed.
    70221: Login status invalid. Please re-authenticate using UserSig.
    70222, 70225, 70231: Internal error. Please retry. If multiple retries still fail, contact TLS account support.
    70236: User signature validation failed.
    70308, 70348, 70362: Internal error. Please retry. If multiple retries still fail, contact TLS account support.
    70346: Ticket validation failed.
    70347: Ticket validation failed due to expiration.
    70401: Internal error. Please retry.
    70402: Invalid parameters. Please check if required fields are filled and if field filling meets protocol requirements.
    70403: Operator is not App administrator, no permission to operate.
    70050: Restricted due to too many failed retries. Please check if the ticket is correct, try again after one minute.
    70051: Account has been blacklisted. Please contact TLS account support.
```

----------------------------------------

TITLE: TRTC Web SDK Error Codes
DESCRIPTION: Provides a comprehensive list of error codes returned by the TRTC Web SDK, indicating various issues such as invalid parameters, device errors, or server problems. Understanding these codes is crucial for debugging and implementing robust error handling in applications.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-03-info-error-code-tips

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE:
  INVALID_PARAMETER
  INVALID_OPERATION
  ENV_NOT_SUPPORTED
  DEVICE_ERROR
  SERVER_ERROR
  OPERATION_FAILED
  OPERATION_ABORT
  UNKNOWN_ERROR
```

----------------------------------------

TITLE: TRTC Web SDK ERROR_CODE Module Constants
DESCRIPTION: Defines a comprehensive list of error codes that can be returned by the TRTC Web SDK, indicating various issues such as invalid parameters, device errors, server errors, and operational failures. These codes help in debugging and handling exceptional conditions.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/TRTC

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Constants:

INVALID_PARAMETER: An invalid parameter was provided to an SDK method.
INVALID_OPERATION: An invalid operation was attempted (e.g., calling a method in an incorrect state).
ENV_NOT_SUPPORTED: The current environment (browser, OS) is not supported.
DEVICE_ERROR: A device-related error occurred (e.g., camera/microphone access denied).
SERVER_ERROR: A server-side error occurred.
OPERATION_FAILED: The operation failed for an unspecified reason.
OPERATION_ABORT: The operation was aborted.
UNKNOWN_ERROR: An unknown error occurred.
```

----------------------------------------

TITLE: Stop Screen Sharing and Handle Events with TRTC Web SDK
DESCRIPTION: Provides the method to stop an active screen share and illustrates how to listen for related events. This includes handling `REMOTE_VIDEO_UNAVAILABLE` when others stop sharing and `SCREEN_SHARE_STOPPED` when the local screen share is terminated by the user or browser.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-16-basic-screencast

LANGUAGE: JavaScript
CODE:
```
// 停止屏幕分享采集及发布
await trtcA.stopScreenShare();
// 房间内的其他用户会收到 TRTC.EVENT.REMOTE_VIDEO_UNAVAILABLE 事件，streamType 是 TRTC.TYPE.STREAM_TYPE_SUB。
trtcB.on(TRTC.EVENT.REMOTE_VIDEO_UNAVAILABLE, ({ userId, streamType }) => {
   if (streamType === TRTC.TYPE.STREAM_TYPE_SUB) {
   }
});

// 监听屏幕分享停止事件
trtcA.on(TRTC.EVENT.SCREEN_SHARE_STOPPED, () => {
  console.log('screen sharing was stopped');
});
```

----------------------------------------

TITLE: TRTC Web SDK ERROR_CODE Module Definitions
DESCRIPTION: Defines various error codes returned by the TRTC Web SDK, indicating issues such as invalid parameters, invalid operations, unsupported environments, device-related problems, server errors, and general operation failures.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-40-advanced-video-mixer

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Definitions:

INVALID_PARAMETER: Invalid parameter provided.
INVALID_OPERATION: Invalid operation performed.
ENV_NOT_SUPPORTED: Environment not supported.
DEVICE_ERROR: Device error occurred.
SERVER_ERROR: Server error occurred.
OPERATION_FAILED: Operation failed.
OPERATION_ABORT: Operation aborted.
UNKNOWN_ERROR: An unknown error occurred.
```

----------------------------------------

TITLE: TRTC SDK Error Codes (ERROR_CODE)
DESCRIPTION: Provides a list of common error codes returned by the TRTC SDK, along with their descriptions. These codes help developers diagnose issues related to invalid parameters, device errors, server problems, and operational failures.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-27-advanced-small-stream

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Error Codes:
  INVALID_PARAMETER: Invalid parameter provided.
  INVALID_OPERATION: Invalid operation performed.
  ENV_NOT_SUPPORTED: Environment not supported.
  DEVICE_ERROR: Device related error.
  SERVER_ERROR: Server side error.
  OPERATION_FAILED: Operation failed.
  OPERATION_ABORT: Operation aborted.
  UNKNOWN_ERROR: Unknown error.
```

----------------------------------------

TITLE: RtcError Class API Reference
DESCRIPTION: API documentation for the RtcError class, detailing its properties for error handling and debugging within the TRTC Web SDK. This class provides structured information about errors encountered during SDK operations.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-12-basic-live-video

LANGUAGE: APIDOC
CODE:
```
RtcError Class Properties:
  - code
  - extraCode
  - functionName
  - message
  - handler
```

----------------------------------------

TITLE: Handle TRTC Screen Share Stopped Event
DESCRIPTION: This event notifies when local screen sharing has stopped. It is only applicable to local screen sharing streams.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/module-EVENT

LANGUAGE: APIDOC
CODE:
```
SCREEN_SHARE_STOPPED Event
Default Value: 'screen-share-stopped'
Description: Local screen sharing stop event notification, only valid for local screen sharing streams.
```

LANGUAGE: JavaScript
CODE:
```
trtc.on(TRTC.EVENT.SCREEN_SHARE_STOPPED, () => {
  console.log('screen sharing was stopped');
});
```

----------------------------------------

TITLE: RtcError Class Properties
DESCRIPTION: This section outlines the properties of the RtcError class, which provides detailed information about errors encountered during TRTC SDK operations. Understanding these properties helps in debugging and implementing robust error handling.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-36-advanced-virtual-background

LANGUAGE: APIDOC
CODE:
```
RtcError Class Properties:

  rtcError.code: number
    - The primary error code, indicating the general type of error.

  rtcError.extraCode: number
    - An additional error code providing more specific details about the error.

  rtcError.functionName: string
    - The name of the SDK function or method where the error occurred.

  rtcError.message: string
    - A human-readable descriptive error message.

  rtcError.handler: Function
    - The error handler function associated with this error, if any.
```

----------------------------------------

TITLE: Managing Coturn TURN Server Service
DESCRIPTION: These commands are used for managing the Coturn TURN server service on a system using `systemd`. They allow starting the service, checking its running status to verify successful deployment, and restarting it for configuration changes or troubleshooting.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-34-advanced-proxy

LANGUAGE: bash
CODE:
```
systemctl start coturn
```

LANGUAGE: bash
CODE:
```
ps aux | grep coturn
```

LANGUAGE: bash
CODE:
```
service coturn restart
```

----------------------------------------

TITLE: RtcError Class API Reference
DESCRIPTION: This section describes the properties of the RtcError class, which is used to provide detailed information about errors encountered during TRTC SDK operations. It helps in debugging and handling specific error conditions.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-11-basic-video-call

LANGUAGE: APIDOC
CODE:
```
RtcError Class Properties:

  code: number
    - The primary error code indicating the type of error.

  extraCode: number
    - An additional error code providing more specific details.

  functionName: string
    - The name of the function or method where the error occurred.

  message: string
    - A human-readable description of the error.

  handler: Function
    - A reference to the error handler function, if applicable.
```

----------------------------------------

TITLE: TRTC Web SDK Error Codes
DESCRIPTION: Defines standard error codes returned by the TRTC Web SDK, indicating various issues such as invalid parameters, device errors, server problems, or unsupported environments. These codes help developers diagnose and troubleshoot problems encountered during SDK operation.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-11-basic-video-call

LANGUAGE: APIDOC
CODE:
```
Module: ERROR_CODE
  INVALID_PARAMETER: Error code for invalid parameters.
  INVALID_OPERATION: Error code for invalid operations.
  ENV_NOT_SUPPORTED: Error code for unsupported environment.
  DEVICE_ERROR: Error code for device errors.
  SERVER_ERROR: Error code for server errors.
  OPERATION_FAILED: Error code for operation failure.
  OPERATION_ABORT: Error code for operation abort.
  UNKNOWN_ERROR: Error code for unknown errors.
```

----------------------------------------

TITLE: Set Log Level for TRTC Web SDK
DESCRIPTION: This static method sets the log output level for the TRTC Web SDK. It's recommended to use DEBUG level during development for detailed information. The default level is INFO. Log upload is enabled by default and should not be turned off as it aids in troubleshooting.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/TRTC

LANGUAGE: APIDOC
CODE:
```
setLogLevel(level, enableUploadLog)
  - Sets the log output level for the SDK.
  - Recommended to set DEBUG level during development. Default is INFO.
  - Parameters:
    level: 0-5 (required) - Log output level.
      0: TRACE
      1: DEBUG
      2: INFO
      3: WARN
      4: ERROR
      5: NONE
    enableUploadLog: boolean (default: true) - Whether to enable log upload. Enabled by default, not recommended to turn off.
```

LANGUAGE: javascript
CODE:
```
// Output log levels above DEBUG
TRTC.setLogLevel(1);
```

----------------------------------------

TITLE: TRTC Web SDK EVENT Module Constants
DESCRIPTION: Lists all events dispatched by the TRTC Web SDK's EVENT module. These events cover a wide range of scenarios including errors, autoplay failures, user kicks, remote user presence changes, media availability (audio/video), volume changes, network quality updates, connection state changes, media play state changes, screen sharing cessation, device changes, publish state changes, track events, statistics, and custom messages.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/module-ERROR_CODE

LANGUAGE: APIDOC
CODE:
```
EVENT Module Constants:

ERROR
  - Description: An error occurred.
AUTOPLAY_FAILED
  - Description: Autoplay of media failed.
KICKED_OUT
  - Description: The user was kicked out of the room.
REMOTE_USER_ENTER
  - Description: A remote user entered the room.
REMOTE_USER_EXIT
  - Description: A remote user exited the room.
REMOTE_AUDIO_AVAILABLE
  - Description: Remote audio is available.
REMOTE_AUDIO_UNAVAILABLE
  - Description: Remote audio is unavailable.
REMOTE_VIDEO_AVAILABLE
  - Description: Remote video is available.
REMOTE_VIDEO_UNAVAILABLE
  - Description: Remote video is unavailable.
AUDIO_VOLUME
  - Description: Audio volume changed.
AUDIO_FRAME
  - Description: An audio frame was received.
NETWORK_QUALITY
  - Description: Network quality changed.
CONNECTION_STATE_CHANGED
  - Description: Connection state changed.
AUDIO_PLAY_STATE_CHANGED
  - Description: Audio playback state changed.
VIDEO_PLAY_STATE_CHANGED
  - Description: Video playback state changed.
SCREEN_SHARE_STOPPED
  - Description: Screen sharing stopped.
DEVICE_CHANGED
  - Description: A media device (camera, microphone) changed.
PUBLISH_STATE_CHANGED
  - Description: Publish state changed.
TRACK
  - Description: Track-related event.
STATISTICS
  - Description: Statistics data available.
SEI_MESSAGE
  - Description: Supplemental Enhancement Information (SEI) message received.
CUSTOM_MESSAGE
  - Description: Custom message received.
FIRST_VIDEO_FRAME
  - Description: First video frame rendered.
```

----------------------------------------

TITLE: RtcError Class API Reference
DESCRIPTION: API documentation for the RtcError class, detailing properties related to error codes, extra codes, function names, messages, and handlers for debugging and error management within the TRTC Web SDK.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-22-advanced-audio-mixer

LANGUAGE: APIDOC
CODE:
```
RtcError Class Properties:

code
  - Type: Number
  - Description: The primary error code.

extraCode
  - Type: Number
  - Description: An additional error code providing more specific details.

functionName
  - Type: String
  - Description: The name of the function where the error occurred.

message
  - Type: String
  - Description: A human-readable error message.

handler
  - Type: Function
  - Description: An optional error handler function.
```

----------------------------------------

TITLE: RtcError Class API Reference
DESCRIPTION: API documentation for the RtcError class, detailing properties related to error codes, additional error information, the function where the error occurred, a descriptive message, and the associated error handler.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-04-info-uplink-limits

LANGUAGE: APIDOC
CODE:
```
RtcError Class:
  code: The error code.
  extraCode: Additional error code information.
  functionName: The name of the function where the error occurred.
  message: A descriptive error message.
  handler: The error handler.
```

----------------------------------------

TITLE: QCloud TRTC Web SDK ERROR_CODE Module Constants
DESCRIPTION: Defines a comprehensive list of error codes returned by the QCloud TRTC Web SDK, indicating various issues such as invalid parameters, device errors, server problems, or operational failures. These codes help in debugging and handling exceptional conditions.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-25-advanced-device-change

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Constants:

INVALID_PARAMETER: Invalid parameter provided.
INVALID_OPERATION: Invalid operation attempted.
ENV_NOT_SUPPORTED: Environment not supported.
DEVICE_ERROR: Media device error.
SERVER_ERROR: Server-side error.
OPERATION_FAILED: Operation failed.
OPERATION_ABORT: Operation aborted.
UNKNOWN_ERROR: An unknown error occurred.
```

----------------------------------------

TITLE: TRTC Web SDK Error Code Definitions
DESCRIPTION: Enumerates common error codes returned by the TRTC Web SDK, providing insights into potential issues such as invalid parameters, unsupported environments, device malfunctions, server-side problems, or general operation failures, aiding in debugging and error handling.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/index

LANGUAGE: APIDOC
CODE:
```
Module: ERROR_CODE
  INVALID_PARAMETER: An invalid parameter was provided.
  INVALID_OPERATION: An invalid operation was attempted.
  ENV_NOT_SUPPORTED: The current environment is not supported.
  DEVICE_ERROR: A media device error occurred.
  SERVER_ERROR: A server-side error occurred.
  OPERATION_FAILED: The operation failed.
  OPERATION_ABORT: The operation was aborted.
  UNKNOWN_ERROR: An unknown error occurred.
```

----------------------------------------

TITLE: TRTC Web SDK ERROR_CODE Module Constants
DESCRIPTION: Defines common error codes returned by the TRTC Web SDK, indicating issues such as invalid parameters, invalid operations, unsupported environments, device errors, server errors, and general operation failures.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-41-advanced-small-stream-auto-switcher

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Constants:

INVALID_PARAMETER: An invalid parameter was provided.
INVALID_OPERATION: An invalid operation was attempted.
ENV_NOT_SUPPORTED: The current environment is not supported.
DEVICE_ERROR: A device-related error occurred.
SERVER_ERROR: A server-side error occurred.
OPERATION_FAILED: The operation failed.
OPERATION_ABORT: The operation was aborted.
UNKNOWN_ERROR: An unknown error occurred.
```

----------------------------------------

TITLE: TRTC Web SDK Event Module Callbacks
DESCRIPTION: Lists all events dispatched by the TRTC Web SDK, providing notifications for errors, user state changes, media availability, network quality, and more. Applications can subscribe to these events to react to changes in the communication session.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-34-advanced-proxy

LANGUAGE: APIDOC
CODE:
```
Module: EVENT
  ERROR: An error occurred.
  AUTOPLAY_FAILED: Autoplay failed.
  KICKED_OUT: User was kicked out.
  REMOTE_USER_ENTER: A remote user entered the room.
  REMOTE_USER_EXIT: A remote user exited the room.
  REMOTE_AUDIO_AVAILABLE: Remote audio is available.
  REMOTE_AUDIO_UNAVAILABLE: Remote audio is unavailable.
  REMOTE_VIDEO_AVAILABLE: Remote video is available.
  REMOTE_VIDEO_UNAVAILABLE: Remote video is unavailable.
  AUDIO_VOLUME: Audio volume changed.
  AUDIO_FRAME: Audio frame received.
  NETWORK_QUALITY: Network quality changed.
  CONNECTION_STATE_CHANGED: Connection state changed.
  AUDIO_PLAY_STATE_CHANGED: Audio playback state changed.
  VIDEO_PLAY_STATE_CHANGED: Video playback state changed.
  SCREEN_SHARE_STOPPED: Screen sharing stopped.
  DEVICE_CHANGED: Device (e.g., camera, mic) changed.
  PUBLISH_STATE_CHANGED: Publish state changed.
  TRACK: Track event.
  STATISTICS: Statistics updated.
  SEI_MESSAGE: SEI message received.
  CUSTOM_MESSAGE: Custom message received.
  FIRST_VIDEO_FRAME: First video frame rendered.
```

----------------------------------------

TITLE: Events for TRTC Web SDK
DESCRIPTION: Lists all events dispatched by the TRTC Web SDK, covering critical notifications such as errors, autoplay failures, user kick-outs, remote user entry/exit, media availability changes (audio/video), audio volume updates, network quality changes, connection state transitions, media play state changes, screen share termination, device changes, publish state changes, track events, statistics updates, and custom messages.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/module-EVENT

LANGUAGE: APIDOC
CODE:
```
Module: EVENT
  ERROR: An error occurred
  AUTOPLAY_FAILED: Autoplay failed
  KICKED_OUT: User was kicked out
  REMOTE_USER_ENTER: A remote user entered the room
  REMOTE_USER_EXIT: A remote user exited the room
  REMOTE_AUDIO_AVAILABLE: Remote audio is available
  REMOTE_AUDIO_UNAVAILABLE: Remote audio is unavailable
  REMOTE_VIDEO_AVAILABLE: Remote video is available
  REMOTE_VIDEO_UNAVAILABLE: Remote video is unavailable
  AUDIO_VOLUME: Audio volume changed
  AUDIO_FRAME: Audio frame received
  NETWORK_QUALITY: Network quality changed
  CONNECTION_STATE_CHANGED: Connection state changed
  AUDIO_PLAY_STATE_CHANGED: Audio play state changed
  VIDEO_PLAY_STATE_CHANGED: Video play state changed
  SCREEN_SHARE_STOPPED: Screen sharing stopped
  DEVICE_CHANGED: Device changed
  PUBLISH_STATE_CHANGED: Publish state changed
  TRACK: Track event
  STATISTICS: Statistics updated
  SEI_MESSAGE: SEI message received
  CUSTOM_MESSAGE: Custom message received
  FIRST_VIDEO_FRAME: First video frame rendered
```

----------------------------------------

TITLE: Handling SDK Automatic Device Acquisition Recovery Failures in TRTC Web SDK
DESCRIPTION: This snippet demonstrates how to handle situations where the SDK's automatic device acquisition recovery fails. It listens for `TRTC.EVENT.ERROR` with specific `TRTC.ERROR_CODE.DEVICE_ERROR` codes (5308 for camera, 5309 for microphone). Upon failure, it prompts the user to check their device and provides guidance on how to manually re-acquire the stream using `updateLocalVideo` or `updateLocalAudio`.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-25-advanced-device-change

LANGUAGE: javascript
CODE:
```
trtc.on(TRTC.EVENT.ERROR, error => {
  if (error.code === TRTC.ERROR_CODE.DEVICE_ERROR) {
    // 摄像头恢复采集失败
    if (error.extraCode === 5308) {
      // 引导用户检查设备后，调用 updateLocalVideo 传入 cameraId 重新采集。
      trtc.updateLocalVideo({ option: { cameraId: '' }});
    }
    // 麦克风恢复采集失败
    if (error.extraCode === 5309) {
      // 引导用户检查设备后，调用 updateLocalAudio 传入 microphoneId 重新采集。
      trtc.updateLocalAudio({ option: { microphoneId: '' }});
    }
  }
})
```

----------------------------------------

TITLE: QCloud TRTC Web SDK Error Code Constants
DESCRIPTION: Defines standard error codes returned by the QCloud TRTC Web SDK, providing specific reasons for failures. These codes help in debugging and handling various operational issues, allowing applications to implement appropriate error recovery or user notifications.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-16-basic-screencast

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Constants:

INVALID_PARAMETER: An invalid parameter was provided.
INVALID_OPERATION: An invalid operation was attempted.
ENV_NOT_SUPPORTED: The current environment is not supported.
DEVICE_ERROR: A device-related error occurred (e.g., camera/mic access).
SERVER_ERROR: A server-side error occurred.
OPERATION_FAILED: The operation failed.
OPERATION_ABORT: The operation was aborted.
UNKNOWN_ERROR: An unknown error occurred.
```

----------------------------------------

TITLE: TRTC AUTOPLAY_FAILED Event Callback Enhancement
DESCRIPTION: In version 5.9.0, the callback parameter for the AUTOPLAY_FAILED event has been enhanced with a new `resume` method. This allows for programmatic attempts to resume autoplay after a failure, improving recovery mechanisms.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-01-info-changelog

LANGUAGE: APIDOC
CODE:
```
EVENT.AUTOPLAY_FAILED
  - Description: Event indicating autoplay failure.
  - Callback Parameter: Now includes a 'resume' method.
  - Usage: callback.resume()
```

----------------------------------------

TITLE: QCloud TRTC Web SDK Error Code Module Constants
DESCRIPTION: Defines a set of error codes returned by the QCloud TRTC Web SDK, providing specific reasons for failures. These codes help in debugging and handling various operational issues, allowing applications to implement appropriate error recovery or user notifications.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-22-advanced-audio-mixer

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Constants:

INVALID_PARAMETER: An invalid parameter was provided.
INVALID_OPERATION: An invalid operation was attempted.
ENV_NOT_SUPPORTED: The current environment is not supported.
DEVICE_ERROR: A media device error occurred.
SERVER_ERROR: A server-side error occurred.
OPERATION_FAILED: The operation failed.
OPERATION_ABORT: The operation was aborted.
UNKNOWN_ERROR: An unknown error occurred.
```

----------------------------------------

TITLE: TRTC Web SDK ERROR_CODE Module Definitions
DESCRIPTION: Enumerates common error codes returned by the TRTC Web SDK's ERROR_CODE module. These codes help identify the cause of issues, such as invalid parameters, unsupported environments, device errors, server-side problems, or general operation failures.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/RtcError

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Definitions:

INVALID_PARAMETER
  - An invalid parameter was provided to an SDK method.
INVALID_OPERATION
  - An operation was attempted that is not valid in the current state.
ENV_NOT_SUPPORTED
  - The current environment (browser, device) is not supported.
DEVICE_ERROR
  - An error occurred with an audio or video device.
SERVER_ERROR
  - A server-side error occurred.
OPERATION_FAILED
  - A general operation failed.
OPERATION_ABORT
  - An operation was aborted.
UNKNOWN_ERROR
  - An unknown error occurred.
```

----------------------------------------

TITLE: Test TRTC Web SDK Uplink and Downlink Network Quality
DESCRIPTION: This JavaScript code demonstrates how to test both uplink and downlink network quality using the TRTC Web SDK. It initializes separate TRTC instances for uplink and downlink, enters a room, listens for `NETWORK_QUALITY` events, and calculates average quality over a 15-second period. The example also shows how to clean up resources by exiting the room after testing.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-24-advanced-network-quality

LANGUAGE: javascript
CODE:
```
let uplinkTRTC = null; // Used to detect uplink network quality
let downlinkTRTC = null; // Used to detect downlink network quality
let localStream = null; // Stream used for testing
let testResult = {
  // Record uplink network quality data
  uplinkNetworkQualities: [],
  // Record downlink network quality data
  downlinkNetworkQualities: [],
  average: {
    uplinkNetworkQuality: 0,
    downlinkNetworkQuality: 0
  }
}
// 1. Test uplink network quality
async function testUplinkNetworkQuality() {
  uplinkTRTC = TRTC.create();
  uplinkTRTC.enterRoom({
    roomId: 8080,
    sdkAppId: 0, // Fill in sdkAppId
    userId: 'user_uplink_test',
    userSig: '', // userSig of uplink_test
    scene: 'rtc'
  })
  uplinkTRTC.on(TRTC.EVENT.NETWORK_QUALITY, event => {
    const { uplinkNetworkQuality } = event;
    testResult.uplinkNetworkQualities.push(uplinkNetworkQuality);
  });
  uplinkTRTC.startLocalVideo();
}
// 2. Detect downlink network quality
async function testDownlinkNetworkQuality() {
  downlinkTRTC = TRTC.create();
  downlinkTRTC.enterRoom({
    roomId: 8080,
    sdkAppId: 0, // Fill in sdkAppId
    userId: 'user_downlink_test',
    userSig: '', // userSig
    scene: 'rtc',
    autoReceiveVideo: true
  });
  downlinkTRTC.on(TRTC.EVENT.NETWORK_QUALITY, event => {
    const { downlinkNetworkQuality } = event;
    testResult.downlinkNetworkQualities.push(downlinkNetworkQuality);
  })
}
// 3. Start detection
testUplinkNetworkQuality();
testDownlinkNetworkQuality();
// 4. Stop detection after 15s and calculate the average network quality
setTimeout(() => {
  // Calculate the average uplink network quality
  const validUplinkNetworkQualitiesList = testResult.uplinkNetworkQualities.filter(value => value >= 1 && value <= 5);
  if (validUplinkNetworkQualitiesList.length > 0) {
    testResult.average.uplinkNetworkQuality = Math.ceil(
      validUplinkNetworkQualitiesList.reduce((value, current) => value + current, 0) / validUplinkNetworkQualitiesList.length
    );
  }
  const validDownlinkNetworkQualitiesList = testResult.uplinkNetworkQualities.filter(value => value >= 1 && value <= 5);
  if (validDownlinkNetworkQualitiesList.length > 0) {
    // Calculate the average downlink network quality
    testResult.average.downlinkNetworkQuality = Math.ceil(
      validDownlinkNetworkQualitiesList.reduce((value, current) => value + current, 0) / validDownlinkNetworkQualitiesList.length
    );
  }
  // Detection is over, clean up related states.
  uplinkTRTC.exitRoom();
  downlinkTRTC.exitRoom();
}, 15 * 1000);
```

----------------------------------------

TITLE: Handle TRTC SDK Device Recovery Failure Events
DESCRIPTION: This snippet demonstrates how to listen for general `TRTC.EVENT.ERROR` events, specifically focusing on device-related errors (`TRTC.ERROR_CODE.DEVICE_ERROR`). It provides logic to handle specific recovery failures for cameras (extraCode 5308) and microphones (extraCode 5309), guiding the application to re-attempt collection after user intervention.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-25-advanced-device-change

LANGUAGE: javascript
CODE:
```
trtc.on(TRTC.EVENT.ERROR, error => {
  if (error.code === TRTC.ERROR_CODE.DEVICE_ERROR) {
    // Camera recovery collection failed
    if (error.extraCode === 5308) {
      // After guiding the user to check the device, call updateLocalVideo and pass in cameraId to recollect.
      trtc.updateLocalVideo({ option: { cameraId: '' }});
    }
    // Microphone recovery collection failed
    if (error.extraCode === 5309) {
      // After guiding the user to check the device, call updateLocalAudio and pass in microphoneId to recollect.
      trtc.updateLocalAudio({ option: { microphoneId: '' }});
    }
  }
})
```

----------------------------------------

TITLE: Configure TRTC Web SDK Proxy Settings for Room Entry
DESCRIPTION: This JavaScript example shows how to configure proxy settings within the TRTC Web SDK when entering a room. It includes options for websocketProxy (for signaling), turnServer (for media relay), iceTransportPolicy, and loggerProxy to ensure communication through a proxy in restricted environments.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-34-advanced-proxy

LANGUAGE: JavaScript
CODE:
```
const trtc = TRTC.create();
await trtc.enterRoom({
  ...,
  proxy: {
    // 设置 Websocket 代理，用于中转 SDK 与 TRTC 后台的信令数据包。
    websocketProxy: 'wss://proxy.example.com/ws/',
    // 设置 turn server，用于中转 SDK 与 TRTC 后台的媒体数据包。14.3.3.3:3478 为 turn server 的 ip 及端口。
    turnServer: { url: '14.3.3.3:3478', username: 'turn', credential: 'turn', credentialType: 'password' },
    // 默认 SDK 会直连 TRTC 服务器，如果连不上，则会尝试连 TURN server。你可以指定 'relay' 来强制连接 TURN server。
    iceTransportPolicy: 'all',
    // SDK 默认会向 yun.tim.qq.com 域名上报日志，但若该域名在您的内网无法访问，您需要给该域名开白名单或者配置以下日志代理。
    // 设置日志上报代理，日志是排查问题的关键数据，请务必设置该代理。
    loggerProxy: 'https://proxy.example.com/logger/',
  }
})
```

----------------------------------------

TITLE: API Reference for EVENT Module Callbacks
DESCRIPTION: Lists all events that can be emitted by the Web SDK, providing notifications for critical occurrences such as errors, autoplay failures, user kicks, remote user entry/exit, audio/video availability changes, audio volume updates, network quality changes, connection state changes, media play state changes, screen share termination, device changes, publish state changes, track events, statistics, and custom messages. Developers can subscribe to these events to react to SDK state changes.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-14-basic-set-video-profile

LANGUAGE: APIDOC
CODE:
```
EVENT Module Callbacks:

ERROR
AUTOPLAY_FAILED
KICKED_OUT
REMOTE_USER_ENTER
REMOTE_USER_EXIT
REMOTE_AUDIO_AVAILABLE
REMOTE_AUDIO_UNAVAILABLE
REMOTE_VIDEO_AVAILABLE
REMOTE_VIDEO_UNAVAILABLE
AUDIO_VOLUME
AUDIO_FRAME
NETWORK_QUALITY
CONNECTION_STATE_CHANGED
AUDIO_PLAY_STATE_CHANGED
VIDEO_PLAY_STATE_CHANGED
SCREEN_SHARE_STOPPED
DEVICE_CHANGED
PUBLISH_STATE_CHANGED
TRACK
STATISTICS
SEI_MESSAGE
CUSTOM_MESSAGE
FIRST_VIDEO_FRAME
```

----------------------------------------

TITLE: Stop TRTC Debug Plugin
DESCRIPTION: This JavaScript snippet illustrates how to stop the `Debug` plugin using the `trtc.stopPlugin()` method. Stopping the plugin disables its active functionalities, such as log collection and the debug pop-up dialog.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-18-basic-debug

LANGUAGE: JavaScript
CODE:
```
trtc.stopPlugin('Debug');
```

----------------------------------------

TITLE: TRTC Web SDK: SCREEN_SHARE_STOPPED Event
DESCRIPTION: Documents the `SCREEN_SHARE_STOPPED` event, which notifies when local screen sharing stops. This event is specifically valid for local screen sharing streams.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/module-EVENT

LANGUAGE: APIDOC
CODE:
```
(static) SCREEN_SHARE_STOPPED
Default Value: 'screen-share-stopped'
Notification event for local screen sharing stop, only valid for local screen sharing streams.
```

LANGUAGE: JavaScript
CODE:
```
trtc.on(TRTC.EVENT.SCREEN_SHARE_STOPPED, () => {
  console.log('screen sharing was stopped');
});
```

----------------------------------------

TITLE: Handle TRTC STATISTICS Event for SDK Metrics
DESCRIPTION: Shows how to subscribe to the `TRTC.EVENT.STATISTICS` event, which provides SDK performance metrics like RTT, uplink, and downlink loss every 2 seconds. This event is crucial for monitoring network quality and audio/video statistics.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/module-EVENT

LANGUAGE: javascript
CODE:
```
trtc.on(TRTC.EVENT.STATISTICS, statistics => {
   console.warn(statistics.rtt, statistics.upLoss, statistics.downLoss);
})
```

----------------------------------------

TITLE: Handle TRTC Web SDK API and Event Errors in JavaScript
DESCRIPTION: This JavaScript example demonstrates how to catch errors from TRTC Web SDK API calls using `.catch()` and how to listen for SDK internal errors via the `TRTC.EVENT.ERROR` event listener. It shows checking `error.code` against predefined `TRTC.ERROR_CODE` constants for specific error handling.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/module-ERROR_CODE

LANGUAGE: JavaScript
CODE:
```
// 使用方式：
// 1. API 调用错误
trtc.startLocalVideo().catch(error => {
 if (error.code === TRTC.ERROR_CODE.DEVICE_ERROR) {}
});
// 2. 非 API 调用错误，SDK 内部经过重试后依然无法恢复的错误
trtc.on(TRTC.EVENT.ERROR, (error) => {
   if (error.code === TRTC.ERROR_CODE.OPERATION_FAILED) {}
});
```

----------------------------------------

TITLE: QCloud TRTC Web SDK Error Codes
DESCRIPTION: Defines standard error codes returned by the QCloud TRTC Web SDK, indicating various issues such as invalid parameters, device errors, or server problems. These codes help developers diagnose and handle issues programmatically.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-37-advanced-voice-changer

LANGUAGE: APIDOC
CODE:
```
ERROR_CODE Module Constants:

INVALID_PARAMETER: Invalid parameter provided.
INVALID_OPERATION: Invalid operation attempted.
ENV_NOT_SUPPORTED: Environment not supported.
DEVICE_ERROR: Device related error.
SERVER_ERROR: Server related error.
OPERATION_FAILED: Operation failed.
OPERATION_ABORT: Operation aborted.
UNKNOWN_ERROR: Unknown error occurred.
```

----------------------------------------

TITLE: RtcError Class API Reference
DESCRIPTION: Documentation for the RtcError class, which provides detailed error information for TRTC SDK operations.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-04-info-uplink-limits

LANGUAGE: APIDOC
CODE:
```
RtcError Class:
  - Properties:
    - code: The error code.
    - extraCode: Additional error code information.
    - functionName: The name of the function where the error occurred.
    - message: A descriptive error message.
    - handler: The error handler.
```

----------------------------------------

TITLE: TRTC Event Listener Updates for Audio and Statistics
DESCRIPTION: Details enhancements to TRTC SDK event listeners, specifically for `AUDIO_FRAME` to access remote audio data and `STATISTICS` to retrieve end-to-end latency metrics, providing more granular control and monitoring capabilities.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-01-info-changelog

LANGUAGE: APIDOC
CODE:
```
EVENT.AUDIO_FRAME
  - Purpose: Provides access to remote audio data.
  - Details: Event triggered when remote audio frame data is available.

EVENT.STATISTICS
  - Purpose: Provides real-time statistics, including end-to-end latency.
  - Details: Event triggered with statistical data about the connection and streams.
```

----------------------------------------

TITLE: TRTC SDK Event Definitions
DESCRIPTION: Lists all events dispatched by the TRTC SDK, covering connection state changes, user presence, audio/video availability, device changes, and various operational notifications.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-00-info-update-guideline

LANGUAGE: APIDOC
CODE:
```
Module: EVENT
  ERROR: General error event.
  AUTOPLAY_FAILED: Autoplay failed event.
  KICKED_OUT: User kicked out event.
  REMOTE_USER_ENTER: Remote user entered the room.
  REMOTE_USER_EXIT: Remote user exited the room.
  REMOTE_AUDIO_AVAILABLE: Remote user's audio stream became available.
  REMOTE_AUDIO_UNAVAILABLE: Remote user's audio stream became unavailable.
  REMOTE_VIDEO_AVAILABLE: Remote user's video stream became available.
  REMOTE_VIDEO_UNAVAILABLE: Remote user's video stream became unavailable.
  AUDIO_VOLUME: Audio volume change event.
  AUDIO_FRAME: Audio frame event.
  NETWORK_QUALITY: Network quality change event.
  CONNECTION_STATE_CHANGED: Connection state changed event.
  AUDIO_PLAY_STATE_CHANGED: Audio playback state changed event.
  VIDEO_PLAY_STATE_CHANGED: Video playback state changed event.
  SCREEN_SHARE_STOPPED: Screen sharing stopped event.
  DEVICE_CHANGED: Device (camera, mic, speaker) changed event.
  PUBLISH_STATE_CHANGED: Publish state changed event.
  TRACK: Track related event.
  STATISTICS: Statistics update event.
  SEI_MESSAGE: SEI (Supplemental Enhancement Information) message received.
  CUSTOM_MESSAGE: Custom message received.
  FIRST_VIDEO_FRAME: First video frame rendered event.
```

----------------------------------------

TITLE: TRTC Web SDK EVENT Module Callbacks
DESCRIPTION: Lists all events that can be emitted by the TRTC Web SDK, allowing applications to respond to various states and occurrences such as errors, user presence, stream availability, network quality changes, device changes, and more.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-12-basic-live-video

LANGUAGE: APIDOC
CODE:
```
EVENT Module Callbacks:

ERROR: An error occurred during SDK operation.
AUTOPLAY_FAILED: Indicates that autoplay of media failed.
KICKED_OUT: The user was kicked out of the room.
REMOTE_USER_ENTER: A remote user entered the room.
REMOTE_USER_EXIT: A remote user exited the room.
REMOTE_AUDIO_AVAILABLE: Remote audio became available.
REMOTE_AUDIO_UNAVAILABLE: Remote audio became unavailable.
REMOTE_VIDEO_AVAILABLE: Remote video became available.
REMOTE_VIDEO_UNAVAILABLE: Remote video became unavailable.
AUDIO_VOLUME: Reports changes in audio volume.
AUDIO_FRAME: An audio frame was received.
NETWORK_QUALITY: Reports changes in network quality.
CONNECTION_STATE_CHANGED: The connection state to the TRTC server changed.
AUDIO_PLAY_STATE_CHANGED: The audio playback state changed.
VIDEO_PLAY_STATE_CHANGED: The video playback state changed.
SCREEN_SHARE_STOPPED: Screen sharing stopped.
DEVICE_CHANGED: A device (e.g., camera, microphone) was changed or disconnected.
PUBLISH_STATE_CHANGED: The publishing state of local streams changed.
TRACK: A track-related event occurred.
STATISTICS: Provides updated statistics about the session.
SEI_MESSAGE: An SEI (Supplemental Enhancement Information) message was received.
CUSTOM_MESSAGE: A custom message was received.
FIRST_VIDEO_FRAME: The first video frame was rendered.
```

----------------------------------------

TITLE: Handle Local Audio Play State Changes (TRTC Web SDK)
DESCRIPTION: This snippet listens for `AUDIO_PLAY_STATE_CHANGED` events to identify problems with the local microphone's collection. It helps in detecting situations where the SDK is trying to recover automatically, enabling the application to advise the user to verify their microphone's status.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-25-advanced-device-change

LANGUAGE: javascript
CODE:
```
trtc.on(TRTC.EVENT.AUDIO_PLAY_STATE_CHANGED, event => {
  // Local microphone collection exception, at this time the SDK will try to automatically recover the collection, you can guide the user to check whether the microphone is normal.
  if (event.userId === '' && (event.reason === 'mute' || event.reason === 'ended')) {}
});
```

----------------------------------------

TITLE: Exit TRTC Room
DESCRIPTION: Exits the current audio/video call room, closing connections to remote users and stopping local audio/video publishing. Local camera/mic capture and preview are not stopped automatically. Call `stopLocalVideo()` and `stopLocalAudio()` to stop local capture.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/TRTC

LANGUAGE: APIDOC
CODE:
```
(async) exitRoom()
  - Description: Exits the current audio/video call room.
  - Throws: OPERATION_ABORT
```

LANGUAGE: JavaScript
CODE:
```
await trtc.exitRoom();
```

----------------------------------------

TITLE: JavaScript Workaround for iOS/Mac Safari Canvas CaptureStream Issues
DESCRIPTION: This JavaScript code provides a conditional workaround for known compatibility issues with `canvas.captureStream` on specific iOS and Mac Safari versions (below iOS 15 or Mac Safari 15+). The `startWaterMark` function stops rendering the video tag and instead appends the canvas directly to the DOM for display. The `stopWaterMark` function reverses this process, removing the canvas and resuming video tag playback, ensuring video visibility across problematic browsers.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-29-advance-water-mark

LANGUAGE: javascript
CODE:
```
// 1. Add the following code to startWaterMark to place the canvas in the DOM for rendering
async function startWaterMark() {
  // ...
  // You can use a third-party userAgent parsing library to determine the version of iOS Mac
  if (IOS_VERSION < 15 || MAC_SAFARI_VERSION >= 15) {
    // Stop rendering the video tag
    await trtc.updateLocalVideo({ view: null });
    // Place the canvas in the DOM for rendering.
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.objectFit = 'cover';
    canvas.style.transform = 'rotateY(180deg)'; // The local video is displayed in mirror image, align here
    // 'local_stream' is the elementId passed in updateLocalVideo({view:elementId})
    document.querySelector('#local_stream').appendChild(canvas);
  }
}
// 2. Add the following code to stopWaterMark. When closing the watermark, remove the canvas and resume using the video tag for playback.
async function stopWaterMark() {
  // ...
  if (IOS_VERSION < 15 || MAC_SAFARI_VERSION >= 15) {
    await trtc.updateLocalVideo({ view: 'elementId' });
    this.canvas.remove();
    this.canvas = null;
  }
}
```

----------------------------------------

TITLE: Handle TRTC Kicked Out Event
DESCRIPTION: This snippet demonstrates how to listen for the `KICKED_OUT` event, which is triggered when a user is forcibly removed from a TRTC room. It logs the reason and message, detailing common kick-out scenarios like duplicate user IDs, administrative bans, or room disbandment.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-11-basic-video-call

LANGUAGE: JavaScript
CODE:
```
trtc.on(TRTC.EVENT.KICKED_OUT, error => {
  console.error(`kicked out, reason:${error.reason}, message:${error.message}`);
  // error.reason has the following situations
  // 'kick' The user with the same userId enters the same room, causing the user who enters the room first to be kicked out.
  // 'banned' The administrator removed the user from the room
  // 'room_disband' The administrator dissolved the room
});
```

----------------------------------------

TITLE: TRTC Web SDK Event Definitions
DESCRIPTION: Lists all events dispatched by the TRTC Web SDK, covering connection states, user presence, media availability, device changes, and message handling. Applications can listen to these events to react to changes in the communication session.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-13-basic-switch-camera-mic

LANGUAGE: APIDOC
CODE:
```
EVENT Module Events:

- ERROR: An error occurred.
- AUTOPLAY_FAILED: Autoplay failed.
- KICKED_OUT: User was kicked out.
- REMOTE_USER_ENTER: A remote user entered the room.
- REMOTE_USER_EXIT: A remote user exited the room.
- REMOTE_AUDIO_AVAILABLE: Remote audio became available.
- REMOTE_AUDIO_UNAVAILABLE: Remote audio became unavailable.
- REMOTE_VIDEO_AVAILABLE: Remote video became available.
- REMOTE_VIDEO_UNAVAILABLE: Remote video became unavailable.
- AUDIO_VOLUME: Audio volume changed.
- AUDIO_FRAME: Audio frame received.
- NETWORK_QUALITY: Network quality changed.
- CONNECTION_STATE_CHANGED: Connection state changed.
- AUDIO_PLAY_STATE_CHANGED: Audio playback state changed.
- VIDEO_PLAY_STATE_CHANGED: Video playback state changed.
- SCREEN_SHARE_STOPPED: Screen sharing stopped.
- DEVICE_CHANGED: Device (e.g., camera, mic) changed.
- PUBLISH_STATE_CHANGED: Publish state changed.
- TRACK: Track event.
- STATISTICS: Statistics updated.
- SEI_MESSAGE: SEI message received.
- CUSTOM_MESSAGE: Custom message received.
- FIRST_VIDEO_FRAME: First video frame rendered.
```

----------------------------------------

TITLE: Handling Virtual Background Plugin Errors in TRTC Web SDK
DESCRIPTION: This JavaScript snippet demonstrates how to handle errors that occur with the 'VirtualBackground' plugin in the TRTC Web SDK. Upon an error, the `onAbort` function is triggered, which can either stop the plugin entirely or suggest lowering the resolution and restarting it to improve performance or resolve rendering issues.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-36-advanced-virtual-background

LANGUAGE: JavaScript
CODE:
```
async function onAbort(error) {
  await trtc.stopPlugin('VirtualBackground'); // Stop the plugin
  // Or lower the resolution and restart the plugin
}
await trtc.startPlugin('VirtualBackground', {
  ...// Other parameters
  onAbort,
});
```

----------------------------------------

TITLE: Configure TRTC Web SDK Proxy Settings
DESCRIPTION: This JavaScript code demonstrates how to configure various proxy settings for the TRTC Web SDK when entering a room. It includes options for WebSocket proxy for signaling, TURN server for media relay, ICE transport policy, and a logger proxy for reporting logs, all aimed at bypassing network restrictions.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-34-advanced-proxy

LANGUAGE: JavaScript
CODE:
```
const trtc = TRTC.create();
await trtc.enterRoom({
  ...,
  proxy: {
    // Set up a Websocket proxy to relay signaling data packets between the SDK and the TRTC backend.
    websocketProxy: 'wss://proxy.example.com/ws/',
    // Set up a turn server to relay media data packets between the SDK and the TRTC backend. 14.3.3.3:3478 is the IP address and port of the turn server.
    turnServer: { url: '14.3.3.3:3478', username: 'turn', credential: 'turn', credentialType: 'password' },
    // By default, the SDK will connect to trtc server directly, if connection failed, then SDK will try to connect the TURN server to relay the media data. You can set 'relay' to force the connection through the TURN server.
    iceTransportPolicy: 'all',
    // By default, the SDK reports logs to the yun.tim.qq.com domain name. If this domain name cannot be accessed in your internal network, you need to whitelist the domain name or configure the following log proxy.
    // Set up a log reporting proxy. Logs are key data for troubleshooting, so be sure to set up this proxy.
    loggerProxy: 'https://proxy.example.com/logger/'
  }
})
```

----------------------------------------

TITLE: Handle Local Video Play State Changes (TRTC Web SDK)
DESCRIPTION: This code snippet listens for `VIDEO_PLAY_STATE_CHANGED` events to detect issues with the local camera's collection state. It specifically targets cases where the SDK attempts automatic recovery (e.g., 'mute' or 'ended' reasons for the main stream), allowing the application to prompt the user to check their camera.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-25-advanced-device-change

LANGUAGE: javascript
CODE:
```
trtc.on(TRTC.EVENT.VIDEO_PLAY_STATE_CHANGED, event => {
  // Local camera collection exception, at this time the SDK will try to automatically recover the collection, you can guide the user to check whether the camera is normal.
  if (event.userId === '' && event.streamType === TRTC.TYPE.STREAM_TYPE_MAIN && (event.reason === 'mute' || event.reason === 'ended')) {}
});
```

----------------------------------------

TITLE: RtcError Class API Reference
DESCRIPTION: API reference for the RtcError class, detailing its properties for error handling and debugging in the TRTC Web SDK.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/tutorial-29-advanced-water-mark

LANGUAGE: APIDOC
CODE:
```
RtcError Class:
  Properties:
    code: The error code.
    extraCode: Additional error code information.
    functionName: The name of the function where the error occurred.
    message: A descriptive error message.
    handler: The error handler.
```

----------------------------------------

TITLE: TRTC Web SDK Event Definitions
DESCRIPTION: Lists all events that can be emitted by the TRTC Web SDK, covering connection states, user presence, media availability, device changes, and various other operational notifications. Developers can subscribe to these events to manage application state and user experience.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-28-advanced-beauty

LANGUAGE: APIDOC
CODE:
```
Module: EVENT
  ERROR: An error occurred.
  AUTOPLAY_FAILED: Autoplay failed.
  KICKED_OUT: User was kicked out of the room.
  REMOTE_USER_ENTER: A remote user entered the room.
  REMOTE_USER_EXIT: A remote user exited the room.
  REMOTE_AUDIO_AVAILABLE: Remote audio became available.
  REMOTE_AUDIO_UNAVAILABLE: Remote audio became unavailable.
  REMOTE_VIDEO_AVAILABLE: Remote video became available.
  REMOTE_VIDEO_UNAVAILABLE: Remote video became unavailable.
  AUDIO_VOLUME: Audio volume changed.
  AUDIO_FRAME: Audio frame received.
  NETWORK_QUALITY: Network quality changed.
  CONNECTION_STATE_CHANGED: Connection state changed.
  AUDIO_PLAY_STATE_CHANGED: Audio play state changed.
  VIDEO_PLAY_STATE_CHANGED: Video play state changed.
  SCREEN_SHARE_STOPPED: Screen sharing stopped.
  DEVICE_CHANGED: Device changed.
  PUBLISH_STATE_CHANGED: Publish state changed.
  TRACK: Track event.
  STATISTICS: Statistics updated.
  SEI_MESSAGE: SEI message received.
  CUSTOM_MESSAGE: Custom message received.
  FIRST_VIDEO_FRAME: First video frame rendered.
```

----------------------------------------

TITLE: TRTC SDK Event Reference
DESCRIPTION: Detailed documentation for key events exposed by the TRTC SDK, including their default values, associated error codes, and usage examples. Events covered include `ERROR` for unrecoverable SDK errors and `AUTOPLAY_FAILED` for handling browser autoplay restrictions.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/module-EVENT

LANGUAGE: APIDOC
CODE:
```
TRTC Event List:

Listen to specific events through trtc.on(TRTC.EVENT.XXX). You can use these events to manage the room user list, manage user stream state, and perceive network state.

Notice:
* Events need to be listened to before they are triggered, so that you can receive the corresponding event notifications. Therefore, it is recommended to complete event listening before entering the room, so as to ensure that no event notifications are missed.

Members:

(static) ERROR
  Default Value: 'error'
  See: RtcError
  Description: Error event, non-API call error, SDK throws when an unrecoverable error occurs during operation.
  Error code (error.code): ErrorCode.OPERATION_FAILED
  Possible extended error codes (error.extraCode): 5501, 5502
  Example:
    trtc.on(TRTC.EVENT.ERROR, error => {
      console.error('trtc error observed: ' + error);
      const errorCode = error.code;
      const extraCode = error.extraCode;
    });

(static) AUTOPLAY_FAILED
  Default Value: 'autoplay-failed'
  Description: Automatic playback failed, refer to Handle Autoplay Restriction
  Details:
    - event.userId: Available since v5.1.3+
    - event.mediaType: Includes 'audio'|'video'|'screen', available since v5.11.0+
    - event.resume(): Call to resume playback, available since v5.9.0+
  Example:
    trtc.on(TRTC.EVENT.AUTOPLAY_FAILED, event => {
      // Guide user to click the page, SDK will resume playback automatically when user click the page.
      // Since v5.1.3+, you can get userId on this event.
      console.log(event.userId);
      // Since v5.11.0+, mediaType includes 'audio'|'video'|'screen'.
      console.log(event.mediaType);
      // Since v5.9.0+, you can call the `resume` method to resume playback of the stream corresponding to event.userId when user clicked the page.
      event.resume();
    });
```

----------------------------------------

TITLE: QCloud TRTC Web SDK EVENT Module Constants
DESCRIPTION: Lists all events dispatched by the QCloud TRTC Web SDK, covering connection states, user presence, media availability, device changes, and more. Developers can listen to these events to manage application logic and UI updates.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-27-advanced-small-stream

LANGUAGE: APIDOC
CODE:
```
EVENT Module Constants:

ERROR
  - Description: An error occurred within the SDK. Event data typically includes an error code and message.
AUTOPLAY_FAILED
  - Description: Autoplay of media failed, often due to browser autoplay policies requiring user interaction.
KICKED_OUT
  - Description: The current user was kicked out of the room by the server or another client.
REMOTE_USER_ENTER
  - Description: A remote user joined the room.
REMOTE_USER_EXIT
  - Description: A remote user left the room.
REMOTE_AUDIO_AVAILABLE
  - Description: A remote user's audio track became available for subscription.
REMOTE_AUDIO_UNAVAILABLE
  - Description: A remote user's audio track became unavailable.
REMOTE_VIDEO_AVAILABLE
  - Description: A remote user's video track became available for subscription.
REMOTE_VIDEO_UNAVAILABLE
  - Description: A remote user's video track became unavailable.
AUDIO_VOLUME
  - Description: Reports the current audio volume levels of local and remote users.
AUDIO_FRAME
  - Description: Raw audio frame data is available, typically used for custom audio processing.
NETWORK_QUALITY
  - Description: Reports the current network quality status (e.g., good, average, poor).
CONNECTION_STATE_CHANGED
  - Description: The connection state to the TRTC service changed (e.g., connecting, connected, disconnected).
AUDIO_PLAY_STATE_CHANGED
  - Description: The playback state of an audio stream changed (e.g., playing, paused).
VIDEO_PLAY_STATE_CHANGED
  - Description: The playback state of a video stream changed (e.g., playing, paused).
SCREEN_SHARE_STOPPED
  - Description: The local screen sharing session was stopped.
DEVICE_CHANGED
  - Description: An input/output device (e.g., camera, microphone, speaker) was added, removed, or changed.
PUBLISH_STATE_CHANGED
  - Description: The publishing state of local streams changed (e.g., publishing, unpublished).
TRACK
  - Description: A media track event, indicating a track was added or removed.
STATISTICS
  - Description: Reports real-time statistics about audio/video streams, such as bitrate, frame rate, and packet loss.
SEI_MESSAGE
  - Description: Received a Supplemental Enhancement Information (SEI) message embedded in a video stream.
CUSTOM_MESSAGE
  - Description: Received a custom message sent by another user.
FIRST_VIDEO_FRAME
  - Description: The first video frame from a remote stream was successfully rendered.
```

----------------------------------------

TITLE: QCloud TRTC Web SDK EVENT Module Constants
DESCRIPTION: Lists all events that can be emitted by the QCloud TRTC Web SDK, providing notifications about connection status, user activity, media availability, device changes, and more. Applications can subscribe to these events to react to SDK state changes.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-25-advanced-device-change

LANGUAGE: APIDOC
CODE:
```
EVENT Module Constants:

ERROR: An error occurred.
AUTOPLAY_FAILED: Autoplay of media failed.
KICKED_OUT: User was kicked out of the room.
REMOTE_USER_ENTER: A remote user entered the room.
REMOTE_USER_EXIT: A remote user exited the room.
REMOTE_AUDIO_AVAILABLE: Remote audio track became available.
REMOTE_AUDIO_UNAVAILABLE: Remote audio track became unavailable.
REMOTE_VIDEO_AVAILABLE: Remote video track became available.
REMOTE_VIDEO_UNAVAILABLE: Remote video track became unavailable.
AUDIO_VOLUME: Audio volume changed.
AUDIO_FRAME: Audio frame data available.
NETWORK_QUALITY: Network quality changed.
CONNECTION_STATE_CHANGED: Connection state changed.
AUDIO_PLAY_STATE_CHANGED: Audio playback state changed.
VIDEO_PLAY_STATE_CHANGED: Video playback state changed.
SCREEN_SHARE_STOPPED: Screen sharing stopped.
DEVICE_CHANGED: Media device (camera, mic) changed.
PUBLISH_STATE_CHANGED: Publish state changed.
TRACK: Track related event.
STATISTICS: Statistics data available.
SEI_MESSAGE: SEI message received.
CUSTOM_MESSAGE: Custom message received.
FIRST_VIDEO_FRAME: First video frame rendered.
```

----------------------------------------

TITLE: Handle TRTC WebRTC SDK Device Capture Errors in JavaScript
DESCRIPTION: This JavaScript example demonstrates how to catch and handle `TRTC.ERROR_CODE.DEVICE_ERROR` when attempting to start local video. It utilizes a `switch` statement to differentiate between specific `extraCode` values, such as 5301 for a missing device or 5302 for permission denial, guiding the application to prompt appropriate user actions or system checks.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/module-ERROR_CODE

LANGUAGE: JavaScript
CODE:
```
trtc.startLocalVideo(...).catch(function(rtcError) {
 if(rtcError.code == TRTC.ERROR_CODE.DEVICE_ERROR) {
   // Guide the user to check the device
   switch(rtcError.extraCode) {
     case 5301:
       // Can't find a camera or microphone, guide the user to check if the microphone and camera are working.
       break;
     case 5302:
       if (error.handler) {
         // Prompt the user the browser permission(camera/microphone/screen sharing) has been denied by system. The browser will jump to the System Settings APP, please enable the relevant permissions!
       } else {
         // Prompt the user to allow camera, microphone, and screen share capture permissions on the page.
       }
       break;
     // ...
   }
 }
})
```

----------------------------------------

TITLE: TRTC SDK Event Constants
DESCRIPTION: Lists various events emitted by the TRTC SDK, covering errors, user presence, audio/video availability, network quality, and device changes. Applications can subscribe to these events to react to changes in the call state or environment.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/zh-cn/module-ERROR_CODE

LANGUAGE: APIDOC
CODE:
```
EVENT Module Constants:

ERROR: An error occurred.
AUTOPLAY_FAILED: Autoplay failed.
KICKED_OUT: User was kicked out.
REMOTE_USER_ENTER: A remote user entered the room.
REMOTE_USER_EXIT: A remote user exited the room.
REMOTE_AUDIO_AVAILABLE: Remote audio is available.
REMOTE_AUDIO_UNAVAILABLE: Remote audio is unavailable.
REMOTE_VIDEO_AVAILABLE: Remote video is available.
REMOTE_VIDEO_UNAVAILABLE: Remote video is unavailable.
AUDIO_VOLUME: Audio volume changed.
AUDIO_FRAME: Audio frame received.
NETWORK_QUALITY: Network quality changed.
CONNECTION_STATE_CHANGED: Connection state changed.
AUDIO_PLAY_STATE_CHANGED: Audio play state changed.
VIDEO_PLAY_STATE_CHANGED: Video play state changed.
SCREEN_SHARE_STOPPED: Screen sharing stopped.
DEVICE_CHANGED: Device changed.
PUBLISH_STATE_CHANGED: Publish state changed.
TRACK: Track event.
STATISTICS: Statistics updated.
SEI_MESSAGE: SEI message received.
CUSTOM_MESSAGE: Custom message received.
FIRST_VIDEO_FRAME: First video frame rendered.
```

----------------------------------------

TITLE: QCloud TRTC WebRTC v5 EVENT Module Definitions
DESCRIPTION: Lists all events dispatched by the QCloud TRTC WebRTC v5 SDK, covering connection states, user presence, media availability, device changes, and more. Applications can listen to these events to react to changes in the SDK's state.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/tutorial-23-advanced-support-detection

LANGUAGE: APIDOC
CODE:
```
EVENT Module Definitions:

ERROR: An error occurred within the SDK.
AUTOPLAY_FAILED: Indicates that media autoplay failed.
KICKED_OUT: The current user was kicked out of the room.
REMOTE_USER_ENTER: A remote user entered the room.
REMOTE_USER_EXIT: A remote user exited the room.
REMOTE_AUDIO_AVAILABLE: A remote audio stream became available.
REMOTE_AUDIO_UNAVAILABLE: A remote audio stream became unavailable.
REMOTE_VIDEO_AVAILABLE: A remote video stream became available.
REMOTE_VIDEO_UNAVAILABLE: A remote video stream became unavailable.
AUDIO_VOLUME: Reports changes in audio volume.
AUDIO_FRAME: Indicates that an audio frame was received.
NETWORK_QUALITY: Reports changes in network quality.
CONNECTION_STATE_CHANGED: The connection state of the SDK changed.
AUDIO_PLAY_STATE_CHANGED: The audio playback state changed.
VIDEO_PLAY_STATE_CHANGED: The video playback state changed.
SCREEN_SHARE_STOPPED: Screen sharing has stopped.
DEVICE_CHANGED: A media device (e.g., camera, microphone) was changed.
PUBLISH_STATE_CHANGED: The publishing state of local streams changed.
TRACK: A track-related event occurred.
STATISTICS: Provides updated statistics from the SDK.
SEI_MESSAGE: An SEI (Supplemental Enhancement Information) message was received.
CUSTOM_MESSAGE: A custom message was received.
FIRST_VIDEO_FRAME: The first video frame was rendered.
```

----------------------------------------

TITLE: TRTC Web SDK EVENT Module Constants
DESCRIPTION: Lists all events dispatched by the TRTC Web SDK, covering connection states, user presence, audio/video availability, device changes, and more. Applications can subscribe to these events to react to changes in the SDK's state and manage the user experience.

SOURCE: https://web.sdk.qcloud.com/trtc/webrtc/v5/doc/zh-cn/index.html/en/module-TYPE

LANGUAGE: APIDOC
CODE:
```
EVENT Module Constants:

ERROR
  - Description: Event indicating an error occurred within the SDK.
AUTOPLAY_FAILED
  - Description: Event indicating that media autoplay failed, often due to browser policies.
KICKED_OUT
  - Description: Event indicating the user was kicked out of the room.
REMOTE_USER_ENTER
  - Description: Event indicating a remote user entered the room.
REMOTE_USER_EXIT
  - Description: Event indicating a remote user exited the room.
REMOTE_AUDIO_AVAILABLE
  - Description: Event indicating that remote audio is now available from a user.
REMOTE_AUDIO_UNAVAILABLE
  - Description: Event indicating that remote audio is no longer available from a user.
REMOTE_VIDEO_AVAILABLE
  - Description: Event indicating that remote video is now available from a user.
REMOTE_VIDEO_UNAVAILABLE
  - Description: Event indicating that remote video is no longer available from a user.
AUDIO_VOLUME
  - Description: Event providing real-time audio volume information.
NETWORK_QUALITY
  - Description: Event providing network quality statistics.
CONNECTION_STATE_CHANGED
  - Description: Event indicating a change in the SDK's connection state.
AUDIO_PLAY_STATE_CHANGED
  - Description: Event indicating a change in the audio playback state.
VIDEO_PLAY_STATE_CHANGED
  - Description: Event indicating a change in the video playback state.
SCREEN_SHARE_STOPPED
  - Description: Event indicating that screen sharing has stopped.
DEVICE_CHANGED
  - Description: Event indicating that an audio or video device has changed.
PUBLISH_STATE_CHANGED
  - Description: Event indicating a change in the stream publishing state.
TRACK
  - Description: Event related to track operations or status.
STATISTICS
  - Description: Event providing detailed statistics about the session.
SEI_MESSAGE
  - Description: Event for receiving SEI (Supplemental Enhancement Information) messages.
CUSTOM_MESSAGE
  - Description: Event for receiving custom messages.
FIRST_VIDEO_FRAME
  - Description: Event indicating that the first video frame has been received and rendered.
```