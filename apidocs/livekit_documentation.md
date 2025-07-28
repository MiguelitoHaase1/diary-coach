# livekit API Documentation

*Fetched using Context7 MCP server on 2025-07-28 10:00:36*

---

========================
CODE SNIPPETS
========================
TITLE: LiveKit Room Class Data Stream and Participant Management
DESCRIPTION: Methods within the LiveKit `Room` class for handling incoming data stream messages, processing stream chunks and trailers, managing RPC and data stream tasks, and retrieving/creating participant objects. It also includes the `__repr__` method for object representation.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/rtc/index

LANGUAGE: python
CODE:
```
                text_reader = TextStreamReader(header)
                self._text_stream_readers[header.stream_id] = text_reader
                text_stream_handler(text_reader, participant_identity)
            elif stream_type == "byte_header":
                byte_stream_handler = self._byte_stream_handlers.get(header.topic)
                if byte_stream_handler is None:
                    logging.info(
                        "ignoring byte stream with topic '%s', no callback attached",
                        header.topic,
                    )
                    return

                byte_reader = ByteStreamReader(header)
                self._byte_stream_readers[header.stream_id] = byte_reader
                byte_stream_handler(byte_reader, participant_identity)
            else:
                logging.warning("received unknown header type, %s", stream_type)
            pass

        async def _handle_stream_chunk(self, chunk: proto_room.DataStream.Chunk):
            text_reader = self._text_stream_readers.get(chunk.stream_id)
            file_reader = self._byte_stream_readers.get(chunk.stream_id)

            if text_reader:
                await text_reader._on_chunk_update(chunk)
            elif file_reader:
                await file_reader._on_chunk_update(chunk)

        async def _handle_stream_trailer(self, trailer: proto_room.DataStream.Trailer):
            text_reader = self._text_stream_readers.get(trailer.stream_id)
            file_reader = self._byte_stream_readers.get(trailer.stream_id)

            if text_reader:
                await text_reader._on_stream_close(trailer)
                self._text_stream_readers.pop(trailer.stream_id)
            elif file_reader:
                await file_reader._on_stream_close(trailer)
                self._byte_stream_readers.pop(trailer.stream_id)

        async def _drain_rpc_invocation_tasks(self) -> None:
            if self._rpc_invocation_tasks:
                for task in self._rpc_invocation_tasks:
                    task.cancel()
                await asyncio.gather(*self._rpc_invocation_tasks, return_exceptions=True)

        async def _drain_data_stream_tasks(self) -> None:
            if self._data_stream_tasks:
                for task in self._data_stream_tasks:
                    task.cancel()
                await asyncio.gather(*self._data_stream_tasks, return_exceptions=True)

        def _retrieve_remote_participant(self, identity: str) -> Optional[RemoteParticipant]:
            """Retrieve a remote participant by identity"""
            return self._remote_participants.get(identity, None)

        def _retrieve_participant(self, identity: str) -> Optional[Participant]:
            """Retrieve a local or remote participant by identity"""
            if identity and identity == self.local_participant.identity:
                return self.local_participant

            return self._retrieve_remote_participant(identity)

        def _create_remote_participant(
            self, owned_info: proto_participant.OwnedParticipant
        ) -> RemoteParticipant:
            if owned_info.info.identity in self._remote_participants:
                raise Exception("participant already exists")

            participant = RemoteParticipant(owned_info)
            self._remote_participants[participant.identity] = participant
            return participant

        def __repr__(self) -> str:
            sid = "unknown"
            if self._first_sid_future.done():
                sid = self._first_sid_future.result()

            return f"rtc.Room(sid={sid}, name={self.name}, metadata={self.metadata}, connection_state={ConnectionState.Name(self._connection_state)})"
```

----------------------------------------

TITLE: Managing LiveKit Room Participants (Python)
DESCRIPTION: Functions for setting and unsetting the active participant for audio/video streams and transcription. These methods handle participant switching, update associated input/output handlers, and manage the internal future for participant availability.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/agents/index

LANGUAGE: Python
CODE:
```
        def set_participant(self, participant_identity: str | None) -> None:
            """Switch audio and video streams to specified participant"""
            if participant_identity is None:
                self.unset_participant()
                return

            if (
                self._participant_identity is not None
                and self._participant_identity != participant_identity
            ):
                # reset future if switching to a different participant
                self._participant_available_fut = asyncio.Future[rtc.RemoteParticipant]()

                # check if new participant is already connected
                for participant in self._room.remote_participants.values():
                    if participant.identity == participant_identity:
                        self._participant_available_fut.set_result(participant)
                        break

            # update participant identity and handlers
            self._participant_identity = participant_identity
            if self._audio_input:
                self._audio_input.set_participant(participant_identity)
            if self._video_input:
                self._video_input.set_participant(participant_identity)

            self._update_transcription_output(self._user_tr_output, participant_identity)

        def unset_participant(self) -> None:
            self._participant_identity = None
            self._participant_available_fut = asyncio.Future[rtc.RemoteParticipant]()
            if self._audio_input:
                self._audio_input.set_participant(None)
            if self._video_input:
                self._video_input.set_participant(None)
            self._update_transcription_output(self._user_tr_output, None)
```

----------------------------------------

TITLE: Initialize LiveKit RoomServiceClient
DESCRIPTION: This snippet demonstrates how to initialize the `RoomServiceClient` in Go. This client is essential for performing all participant management operations and requires the LiveKit host URL, API key, and secret key for authentication.

SOURCE: https://docs.livekit.io/home/server/managing-participants

LANGUAGE: Go
CODE:
```
import (
	lksdk "github.com/livekit/server-sdk-go"
	livekit "github.com/livekit/protocol/livekit"
)

// ...
host := "https://my.livekit.host"
roomClient := lksdk.NewRoomServiceClient(host, "api-key", "secret-key")
```

----------------------------------------

TITLE: List Participants in a LiveKit Room
DESCRIPTION: This snippet shows how to retrieve a list of all participants currently present in a specified LiveKit room. It uses the `ListParticipants` method of the `RoomServiceClient` and requires the room name.

SOURCE: https://docs.livekit.io/home/server/managing-participants

LANGUAGE: Go
CODE:
```
res, err := roomClient.ListParticipants(context.Background(), &livekit.ListParticipantsRequest{
	Room: roomName,
})
```

----------------------------------------

TITLE: Handle Participant Connected Event in LiveKit Room
DESCRIPTION: Demonstrates how to register a callback function to handle the 'participant_connected' event in a LiveKit room, printing the participant's identity when they connect.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/rtc/room

LANGUAGE: Python
CODE:
```
def on_participant_connected(participant):
    print(f"Participant connected: {participant.identity}")

room.on("participant_connected", on_participant_connected)
```

----------------------------------------

TITLE: Send Data to LiveKit Room Participants
DESCRIPTION: Sends a data payload to participants in a LiveKit room. It allows specifying the room, data, delivery kind (reliable or lossy), target participant identities, and an optional topic.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: Python
CODE:
```
        async def send_data(self, send: SendDataRequest) -> SendDataResponse:
            """Sends data to participants in a room.

            Args:
                send (SendDataRequest): arg containing:
                    - room: str - Room name
                    - data: bytes - Data payload to send
                    - kind: DataPacket.Kind - RELIABLE or LOSSY delivery
                    - destination_identities: list[str] - Target participant identities
                    - topic: str - Optional topic for the message

            Returns:
                SendDataResponse: Empty response object
            """

            send.nonce = uuid4().bytes
            return await self._client.request(
                SVC,
                "SendData",
                send,
                self._auth_header(VideoGrants(room_admin=True, room=send.room)),
                SendDataResponse,
            )
```

LANGUAGE: APIDOC
CODE:
```
async def send_data(
  send: room.SendDataRequest
) -> room.SendDataResponse:
  Args:
    send (SendDataRequest):
      room: str - Room name
      data: bytes - Data payload to send
      kind: DataPacket.Kind - RELIABLE or LOSSY delivery
      destination_identities: list[str] - Target participant identities
      topic: str - Optional topic for the message
  Returns:
    SendDataResponse: Empty response object
```

----------------------------------------

TITLE: LiveKit Room Connection and Participant Initialization (Python)
DESCRIPTION: This code snippet illustrates the post-connection setup for a LiveKit room, including initializing FFI handles, E2EE management, updating connection state, and populating local and remote participant information. It also sets up initial track publications for remote participants.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/rtc/index

LANGUAGE: Python
CODE:
```
                FfiClient.instance.queue.unsubscribe(self._ffi_queue)
                raise ConnectError(cb.connect.error)

            self._ffi_handle = FfiHandle(cb.connect.result.room.handle.id)

            self._e2ee_manager = E2EEManager(self._ffi_handle.handle, options.e2ee)

            self._info = cb.connect.result.room.info
            self._connection_state = ConnectionState.CONN_CONNECTED

            self._local_participant = LocalParticipant(
                self._room_queue, cb.connect.result.local_participant
            )

            for pt in cb.connect.result.participants:
                rp = self._create_remote_participant(pt.participant)

                # add the initial remote participant tracks
                for owned_publication_info in pt.publications:
                    publication = RemoteTrackPublication(owned_publication_info)
                    rp._track_publications[publication.sid] = publication

            # start listening to room events
            self._task = self._loop.create_task(self._listen_task())
```

----------------------------------------

TITLE: List LiveKit Room Participants (Python)
DESCRIPTION: Fetches a list of all participants currently in a specified LiveKit room. This method requires room administration privileges and takes a `ListParticipantsRequest` object, returning a `ListParticipantsResponse`.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: python
CODE:
```
async def list_participants(self, list: ListParticipantsRequest) -> ListParticipantsResponse:
    """Lists all participants in a room.

    Args:
        list (ListParticipantsRequest): arg containing:
            - room: str - Name of room to list participants from

    Returns:
        ListParticipantsResponse:
            - participants: list[ParticipantInfo] - List of participant details
    """
    return await self._client.request(
        SVC,
        "ListParticipants",
        list,
        self._auth_header(VideoGrants(room_admin=True, room=list.room)),
        ListParticipantsResponse,
    )
```

LANGUAGE: APIDOC
CODE:
```
Method: list_participants
Description: Lists all participants in a room.
Parameters:
  list (ListParticipantsRequest):
    - room (str): Name of room to list participants from
Returns:
  ListParticipantsResponse:
    - participants (list[ParticipantInfo]): List of participant details
```

----------------------------------------

TITLE: Remove LiveKit Room Participant (Go)
DESCRIPTION: Illustrates how to forcibly disconnect a participant from a LiveKit room using the Go SDK. This action does not invalidate the participant's token, so measures like short TTLs or not re-issuing tokens are recommended to prevent rejoining.

SOURCE: https://docs.livekit.io/home/server/managing-participants

LANGUAGE: Go
CODE:
```
res, err := roomClient.RemoveParticipant(context.Background(), &livekit.RoomParticipantIdentity{

Room:     roomName,

Identity: identity,

})
```

----------------------------------------

TITLE: Python Function: Handle Remote Participant Connection
DESCRIPTION: Callback function invoked when a remote participant connects to the room. If a linked participant is not already set, it attempts to link to the newly connected participant using their identity, delegating to '_link_participant'.

SOURCE: https://docs.livekit.io/reference/python/livekit/agents/multimodal/multimodal_agent

LANGUAGE: python
CODE:
```
def _on_participant_connected(self, participant: rtc.RemoteParticipant):
    if self._linked_participant is None:
        return

    self._link_participant(participant.identity)
```

----------------------------------------

TITLE: Initialize Participant Management Task
DESCRIPTION: An asynchronous initialization task that waits for the room to be connected. It then checks for existing remote participants, sets the active participant, and initializes transcription outputs and audio output streams. This method ensures the system is ready to handle participant interactions.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/agents

LANGUAGE: python
CODE:
```
@utils.log_exceptions(logger=logger)
async def _init_task(self) -> None:
    await self._room_connected_fut

    # check existing participants
    for participant in self._room.remote_participants.values():
        self._on_participant_connected(participant)

    participant = await self._participant_available_fut
    self.set_participant(participant.identity)

    # init outputs
    self._update_transcription_output(
        self._agent_tr_output, self._room.local_participant.identity
    )
    if self._audio_output:
        await self._audio_output.start()
```

----------------------------------------

TITLE: ListParticipants API Endpoint
DESCRIPTION: List participants in a room, Requires `roomAdmin`

SOURCE: https://docs.livekit.io/reference/server/server-apis

LANGUAGE: APIDOC
CODE:
```
ListParticipants
Returns: List<ParticipantInfo>
  room: string (Required) - name of the room
```

----------------------------------------

TITLE: LiveKit Room Internal Data Stream and Participant Management
DESCRIPTION: This Python code defines internal methods for handling data stream chunks and trailers, draining asynchronous tasks, and retrieving/creating remote participants within a LiveKit `Room` instance. It demonstrates how the SDK manages various aspects of real-time communication.

SOURCE: https://docs.livekit.io/reference/python/livekit/rtc/room

LANGUAGE: Python
CODE:
```
                byte_stream_handler(byte_reader, participant_identity)
            else:
                logging.warning("received unknown header type, %s", stream_type)
            pass

        async def _handle_stream_chunk(self, chunk: proto_room.DataStream.Chunk):
            text_reader = self._text_stream_readers.get(chunk.stream_id)
            file_reader = self._byte_stream_readers.get(chunk.stream_id)

            if text_reader:
                await text_reader._on_chunk_update(chunk)
            elif file_reader:
                await file_reader._on_chunk_update(chunk)

        async def _handle_stream_trailer(self, trailer: proto_room.DataStream.Trailer):
            text_reader = self._text_stream_readers.get(trailer.stream_id)
            file_reader = self._byte_stream_readers.get(trailer.stream_id)

            if text_reader:
                await text_reader._on_stream_close(trailer)
                self._text_stream_readers.pop(trailer.stream_id)
            elif file_reader:
                await file_reader._on_stream_close(trailer)
                self._byte_stream_readers.pop(trailer.stream_id)

        async def _drain_rpc_invocation_tasks(self) -> None:
            if self._rpc_invocation_tasks:
                for task in self._rpc_invocation_tasks:
                    task.cancel()
                await asyncio.gather(*self._rpc_invocation_tasks, return_exceptions=True)

        async def _drain_data_stream_tasks(self) -> None:
            if self._data_stream_tasks:
                for task in self._data_stream_tasks:
                    task.cancel()
                await asyncio.gather(*self._data_stream_tasks, return_exceptions=True)

        def _retrieve_remote_participant(self, identity: str) -> Optional[RemoteParticipant]:
            """Retrieve a remote participant by identity"""
            return self._remote_participants.get(identity, None)

        def _retrieve_participant(self, identity: str) -> Optional[Participant]:
            """Retrieve a local or remote participant by identity"""
            if identity and identity == self.local_participant.identity:
                return self.local_participant

            return self._retrieve_remote_participant(identity)

        def _create_remote_participant(
            self, owned_info: proto_participant.OwnedParticipant
        ) -> RemoteParticipant:
            if owned_info.info.identity in self._remote_participants:
                raise Exception("participant already exists")

            participant = RemoteParticipant(owned_info)
            self._remote_participants[participant.identity] = participant
            return participant

        def __repr__(self) -> str:
            sid = "unknown"
            if self._first_sid_future.done():
                sid = self._first_sid_future.result()

            return f"rtc.Room(sid={sid}, name={self.name}, metadata={self.metadata}, connection_state={ConnectionState.Name(self._connection_state)})"
```

----------------------------------------

TITLE: Update LiveKit Participant Metadata (Go)
DESCRIPTION: Demonstrates how to update a participant's metadata in a LiveKit room using the Go SDK. This operation triggers a `ParticipantMetadataChanged` event for connected clients. It requires the room name, participant identity, and the new metadata as a string.

SOURCE: https://docs.livekit.io/home/server/managing-participants

LANGUAGE: Go
CODE:
```
data, err := json.Marshal(values)

_, err = c.UpdateParticipant(context.Background(), &livekit.UpdateParticipantRequest{

Room: roomName,

Identity: identity,

Metadata: string(data),

})
```

----------------------------------------

TITLE: UpdateParticipant API Endpoint
DESCRIPTION: Update information for a participant. Updating metadata will broadcast the change to all other participants in the room. Requires `roomAdmin`

SOURCE: https://docs.livekit.io/reference/server/server-apis

LANGUAGE: APIDOC
CODE:
```
UpdateParticipant
  room: string (Required) -
  identity: string (Required) -
  metadata: string - user-provided payload, an empty value is equivalent to a no-op
  permission: ParticipantPermission - set to update the participant's permissions
```

----------------------------------------

TITLE: GetParticipant API Endpoint
DESCRIPTION: Get information about a specific participant in a room, Requires `roomAdmin`

SOURCE: https://docs.livekit.io/reference/server/server-apis

LANGUAGE: APIDOC
CODE:
```
GetParticipant
Returns: ParticipantInfo
  room: string (Required) - name of the room
  identity: string (Required) - identity of the participant
```

----------------------------------------

TITLE: Room Class: participants Property API Documentation
DESCRIPTION: Documents the `participants` property of the `Room` class, which provides an unmodifiable map of remote participants. The map keys are participant SIDs (String) and values are `RemoteParticipant` objects.

SOURCE: https://docs.livekit.io/reference/client-sdk-flutter/livekit_client/Room/participants

LANGUAGE: APIDOC
CODE:
```
Class: Room
  Property: participants
    Type: UnmodifiableMapView<String, RemoteParticipant>
    Description: An unmodifiable map containing remote participants in the room. Keys are participant SIDs (String), and values are RemoteParticipant objects.
```

----------------------------------------

TITLE: LiveKit Room Service: forward_participant
DESCRIPTION: API documentation for forwarding a participant between LiveKit rooms. Outlines the required parameters for source and destination rooms, and participant identity.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: APIDOC
CODE:
```
async def forward_participant(self, forward: room.ForwardParticipantRequest) -> None
  forward: ForwardParticipantRequest
    - room: str - Room name
    - identity: str - identity of Participant to forward
    - destination_room: str - Destination room name
```

----------------------------------------

TITLE: Get LiveKit Room Participant Details (Python)
DESCRIPTION: Retrieves detailed information about a specific participant in a LiveKit room. This method requires room administration privileges and takes a `RoomParticipantIdentity` object as input, returning a `ParticipantInfo` object.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: python
CODE:
```
async def get_participant(self, get: RoomParticipantIdentity) -> ParticipantInfo:
    """Gets details about a specific participant.

    Args:
        get (RoomParticipantIdentity): arg containing:
            - room: str - Room name
            - identity: str - Participant identity to look up

    Returns:
        ParticipantInfo:
            - sid: str - Participant session ID
            - identity: str - Participant identity
            - state: int - Connection state
            - tracks: list[TrackInfo] - Published tracks
            - metadata: str - Participant metadata
            - joined_at: int - Join timestamp
            - name: str - Display name
            - version: int - Protocol version
            - permission: ParticipantPermission - Granted permissions
            - region: str - Connected region
    """
    return await self._client.request(
        SVC,
        "GetParticipant",
        get,
        self._auth_header(VideoGrants(room_admin=True, room=get.room)),
        ParticipantInfo,
    )
```

LANGUAGE: APIDOC
CODE:
```
Method: get_participant
Description: Gets details about a specific participant.
Parameters:
  get (RoomParticipantIdentity):
    - room (str): Room name
    - identity (str): Participant identity to look up
Returns:
  ParticipantInfo:
    - sid (str): Participant session ID
    - identity (str): Participant identity
    - state (int): Connection state
    - tracks (list[TrackInfo]): Published tracks
    - metadata (str): Participant metadata
    - joined_at (int): Join timestamp
    - name (str): Display name
    - version (int): Protocol version
    - permission (ParticipantPermission): Granted permissions
    - region (str): Connected region
```

----------------------------------------

TITLE: Detect LiveKit Active Speakers and Speaking Status Changes (JavaScript)
DESCRIPTION: Shows how to implement active speaker identification by listening to `RoomEvent.ActiveSpeakersChanged` on the `Room` object and `ParticipantEvent.IsSpeakingChanged` on individual `Participant` objects. This allows UI updates based on who is currently speaking.

SOURCE: https://docs.livekit.io/home/client/tracks/subscribe

LANGUAGE: JavaScript
CODE:
```
room.on(RoomEvent.ActiveSpeakersChanged, (speakers: Participant[]) => {
// Speakers contain all of the current active speakers
});

participant.on(ParticipantEvent.IsSpeakingChanged, (speaking: boolean) => {
console.log(
`${participant.identity} is ${speaking ? 'now' : 'no longer'} speaking. audio level: ${participant.audioLevel}`,
);
});
```

----------------------------------------

TITLE: LiveKit Room Service API: Update Participant
DESCRIPTION: Documents the `update_participant` method for modifying a participant's metadata or permissions within a room, along with its Python implementation.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: APIDOC
CODE:
```
update_participant(update: UpdateParticipantRequest) -> ParticipantInfo
  Description: Updates a participant's metadata or permissions.
  Parameters:
    update (UpdateParticipantRequest):
      - room: str - Room name
      - identity: str - Participant identity
      - metadata: str - New metadata
      - permission: ParticipantPermission - New permissions
      - name: str - New display name
      - attributes: dict[str, str] - Key-value attributes
  Returns:
    ParticipantInfo: Updated participant information
```

LANGUAGE: python
CODE:
```
return await self._client.request(
    SVC,
    "UpdateParticipant",
    update,
    self._auth_header(VideoGrants(room_admin=True, room=update.room)),
    ParticipantInfo,
)
```

----------------------------------------

TITLE: Create LiveKit Room
DESCRIPTION: Creates a new room with specified configuration using the LiveKit API client. This method handles authentication and returns the created room object.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: python
CODE:
```
async def create_room(
    self,
    create: CreateRoomRequest,
) -> Room:
    """Creates a new room with specified configuration.

    Args:
        create (CreateRoomRequest): arg containing:
            - name: str - Unique room name
            - empty_timeout: int - Seconds to keep room open if empty
            - max_participants: int - Max allowed participants
            - metadata: str - Custom room metadata
            - egress: RoomEgress - Egress configuration
            - min_playout_delay: int - Minimum playout delay in ms
            - max_playout_delay: int - Maximum playout delay in ms
            - sync_streams: bool - Enable A/V sync for playout delays >200ms

    Returns:
        Room: The created room object
    """
    return await self._client.request(
        SVC,
        "CreateRoom",
        create,
        self._auth_header(VideoGrants(room_create=True)),
        Room,
    )
```

----------------------------------------

TITLE: Get Room Remote Participants (Python)
DESCRIPTION: Retrieves a mapping of remote participants in the LiveKit room, indexed by their identity. This allows access to other users in the room.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/rtc/index

LANGUAGE: Python
CODE:
```
@property
def remote_participants(self) -> Mapping[str, RemoteParticipant]:
    """Gets the remote participants in the room.

    Returns:
        dict[str, RemoteParticipant]: A dictionary of remote participants indexed by their
        identity.
    """
    return self._remote_participants
```

----------------------------------------

TITLE: Handle Participant Availability in LiveKit Room in Python
DESCRIPTION: A private helper method invoked when a participant becomes available in the room. This method is likely part of the internal logic for managing participant lifecycle events.

SOURCE: https://docs.livekit.io/reference/python/livekit/agents/index

LANGUAGE: python
CODE:
```
def _participant_available(self, p: rtc.RemoteParticipant) -> None:
```

----------------------------------------

TITLE: Retrieve Core Participant Properties
DESCRIPTION: Provides access to fundamental participant attributes such as unique identity, participant kind (e.g., ingress, egress, sip, agent), associated metadata, display name, and session ID. These properties are read-only and reflect the participant's current state within the room.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/rtc/participant

LANGUAGE: python
CODE:
```
@property
def identity(self) -> str:
    return self._info.identity
```

LANGUAGE: python
CODE:
```
@property
def kind(self) -> proto_participant.ParticipantKind.ValueType:
    """Participant's kind (e.g., regular participant, ingress, egress, sip, agent)."""
    return self._info.kind
```

LANGUAGE: python
CODE:
```
@property
def metadata(self) -> str:
    return self._info.metadata
```

LANGUAGE: python
CODE:
```
@property
def name(self) -> str:
    return self._info.name
```

LANGUAGE: python
CODE:
```
@property
def sid(self) -> str:
    return self._info.sid
```

----------------------------------------

TITLE: Get Details of a Specific LiveKit Participant
DESCRIPTION: This snippet illustrates how to fetch detailed information about a single participant in a LiveKit room. It uses the `GetParticipant` method, requiring both the room name and the participant's identity.

SOURCE: https://docs.livekit.io/home/server/managing-participants

LANGUAGE: Go
CODE:
```
res, err := roomClient.GetParticipant(context.Background(), &livekit.RoomParticipantIdentity{
	Room:     roomName,
	Identity: identity,
})
```

----------------------------------------

TITLE: Mute/Unmute LiveKit Participant Track (Go)
DESCRIPTION: Shows how to mute or unmute a specific track for a participant in a LiveKit room using the Go SDK. This requires the room name, participant identity, and the track SID. Remote unmute is disabled by default and requires explicit configuration in project settings or server YAML.

SOURCE: https://docs.livekit.io/home/server/managing-participants

LANGUAGE: Go
CODE:
```
res, err := roomClient.MutePublishedTrack(context.Background(), &livekit.MuteRoomTrackRequest{

Room:     roomName,

Identity: identity,

TrackSid: "track_sid",

Muted:    true,

})
```

----------------------------------------

TITLE: LiveKit Room Initialization and Connection Event Handling (Python)
DESCRIPTION: Asynchronous methods for initializing the room state, handling connection state changes, and managing participant connection/disconnection events. These functions ensure the internal state reflects the current room and participant status, including setting up transcription outputs.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/agents/index

LANGUAGE: Python
CODE:
```
        @utils.log_exceptions(logger=logger)
        async def _init_task(self) -> None:
            await self._room_connected_fut

            # check existing participants
            for participant in self._room.remote_participants.values():
                self._on_participant_connected(participant)

            participant = await self._participant_available_fut
            self.set_participant(participant.identity)

            # init outputs
            self._update_transcription_output(
                self._agent_tr_output, self._room.local_participant.identity
            )
            if self._audio_output:
                await self._audio_output.start()

        def _on_connection_state_changed(self, state: rtc.ConnectionState.ValueType) -> None:
            if self._room.isconnected() and not self._room_connected_fut.done():
                self._room_connected_fut.set_result(None)

        def _on_participant_connected(self, participant: rtc.RemoteParticipant) -> None:
            if self._participant_available_fut.done():
                return

            if self._participant_identity is not None:
                if participant.identity != self._participant_identity:
                    return
            # otherwise, skip participants that are marked as publishing for this agent
            elif (
                participant.attributes.get(ATTRIBUTE_PUBLISH_ON_BEHALF)
                == self._room.local_participant.identity
            ):
                return

            accepted_kinds = self._input_options.participant_kinds or DEFAULT_PARTICIPANT_KINDS
            if participant.kind not in accepted_kinds:
                # not an accepted participant kind, skip
                return

            self._participant_available_fut.set_result(participant)

        def _on_participant_disconnected(self, participant: rtc.RemoteParticipant) -> None:
            if not (linked := self.linked_participant) or participant.identity != linked.identity:
                return

            self._participant_available_fut = asyncio.Future[rtc.RemoteParticipant]()

            if (
                self._input_options.close_on_disconnect
                and participant.disconnect_reason in DEFAULT_CLOSE_ON_DISCONNECT_REASONS
                and not self._close_session_atask
            )
```

----------------------------------------

TITLE: LiveKit Room Participant and State Accessors
DESCRIPTION: Provides properties to access the local participant, current connection state, and a mapping of remote participants within the LiveKit room. Throws an exception if the local participant is accessed before connection.

SOURCE: https://docs.livekit.io/reference/python/livekit/rtc/index

LANGUAGE: Python
CODE:
```
@property
def local_participant(self) -> LocalParticipant:
    """Gets the local participant in the room.

    Returns:
        LocalParticipant: The local participant in the room.
    """
    if self._local_participant is None:
        raise Exception("cannot access local participant before connecting")

    return self._local_participant

@property
def connection_state(self) -> ConnectionState.ValueType:
    """Gets the connection state of the room.

    Returns:
        ConnectionState: The connection state of the room.
    """
    return self._connection_state

@property
def remote_participants(self) -> Mapping[str, RemoteParticipant]:
    """Gets the remote participants in the room.

    Returns:
        dict[str, RemoteParticipant]: A dictionary of remote participants indexed by their
        identity.
    """
    return self._remote_participants
```

----------------------------------------

TITLE: API Documentation for Room
DESCRIPTION: Provides a comprehensive overview of the Room class, detailing methods for connecting, disconnecting, managing participants, and handling events within a LiveKit room.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/rtc/index

LANGUAGE: APIDOC
CODE:
```
Room:
  connect
  connection_state
  disconnect
  e2ee_manager
  get_rtc_stats
  isconnected
  local_participant
  metadata
  name
  on
  register_byte_stream_handler
  register_text_stream_handler
  remote_participants
  sid
  unregister_byte_stream_handler
  unregister_text_stream_handler
```

----------------------------------------

TITLE: Register LiveKit Room Participant Connected Event
DESCRIPTION: Demonstrates how to register a callback function to handle the "participant_connected" event on a LiveKit Room object. The callback receives the `participant` object when a new participant connects to the room.

SOURCE: https://docs.livekit.io/reference/python/livekit/rtc/room

LANGUAGE: Python
CODE:
```
def on_participant_connected(participant):
    print(f"Participant connected: {participant.identity}")

room.on("participant_connected", on_participant_connected)
```

----------------------------------------

TITLE: LiveKit Android Room: Accessing Local Participant Property
DESCRIPTION: This API documentation describes the `localParticipant` property available in the `io.livekit.android.room.Room` class. It provides a reference to the `LocalParticipant` object, which represents the current user in the LiveKit room and allows for managing local media tracks and publishing.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room/-room/local-participant

LANGUAGE: APIDOC
CODE:
```
Class: io.livekit.android.room.Room
  Property: localParticipant
    Type: io.livekit.android.room.participant.LocalParticipant
    Description: Represents the current user's participant in the room, providing control over local media and publishing.
    Declaration: val localParticipant: LocalParticipant
```

----------------------------------------

TITLE: LiveKit Room Class API Reference
DESCRIPTION: Detailed API documentation for the `Room` class, which represents a logical grouping for participants in LiveKit. It covers the constructor for initializing a room, various properties reflecting its state and participants, accessors for derived information, and methods for interacting with a LiveKit room, including connection management, media handling, and participant operations.

SOURCE: https://docs.livekit.io/reference/client-sdk-js/classes/Room

LANGUAGE: APIDOC
CODE:
```
Class Room:
  Description: In LiveKit, a room is the logical grouping for a list of participants. Participants in a room can publish tracks, and subscribe to others' tracks.
  Hierarchy: TypedEventEmitter<RoomEventCallbacks, this> + Room

  Constructors:
    constructor(options?: RoomOptions): Room
      Description: Creates a new Room, the primary construct for a LiveKit session.
      Parameters:
        options: RoomOptions (Optional)
      Returns: Room

  Properties:
    activeSpeakers: Participant[] = []
      Description: list of participants that are actively speaking. when this changes a RoomEvent.ActiveSpeakersChanged event is fired
    bufferedSegments: Map<string, TranscriptionSegment> = ...
    isE2EEEnabled: boolean = false
      Description: reflects the sender encryption status of the local participant
    localParticipant: LocalParticipant
      Description: the current participant
    options: InternalRoomOptions
      Description: options of room
    remoteParticipants: Map<string, RemoteParticipant>
      Description: map of identity: RemoteParticipant
    serverInfo?: Partial<ServerInfo>
    state: ConnectionState = ConnectionState.Disconnected
    cleanupRegistry: false | FinalizationRegistry<() => void> = ... (Static)

  Accessors:
    get canPlaybackAudio(): boolean
      Description: Returns true if audio playback is enabled
      Returns: boolean
    get canPlaybackVideo(): boolean
    get isRecording(): boolean
    get metadata(): any
    get name(): string
    get numParticipants(): number
    get numPublishers(): number

  Methods:
    connect()
    disconnect()
    emit()
    getActiveDevice()
    getParticipantByIdentity()
    getSid()
    prepareConnection()
    registerByteStreamHandler()
    registerRpcMethod()
    registerTextStreamHandler()
    setE2EEEnabled()
    simulateParticipants()
    startAudio()
    startVideo()
    switchActiveDevice()
    unregisterByteStreamHandler()
    unregisterRpcMethod()
    unregisterTextStreamHandler()
    getLocalDevices()
```

----------------------------------------

TITLE: Remove LiveKit Room Participant
DESCRIPTION: Removes a participant from a LiveKit room. This operation requires room admin privileges and specifies the room and identity of the participant to remove.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: Python
CODE:
```
        async def remove_participant(
            self, remove: RoomParticipantIdentity
        ) -> RemoveParticipantResponse:
            """Removes a participant from a room.

            Args:
                remove (RoomParticipantIdentity): arg containing:
                    - room: str - Room name
                    - identity: str - Identity of participant to remove

            Returns:
                RemoveParticipantResponse: Empty response object
            """
            return await self._client.request(
                SVC,
                "RemoveParticipant",
                remove,
                self._auth_header(VideoGrants(room_admin=True, room=remove.room)),
                RemoveParticipantResponse,
            )
```

LANGUAGE: APIDOC
CODE:
```
async def remove_participant(
  remove: room.RoomParticipantIdentity
) -> room.RemoveParticipantResponse:
  Args:
    remove (RoomParticipantIdentity):
      room: str - Room name
      identity: str - Identity of participant to remove
  Returns:
    RemoveParticipantResponse: Empty response object
```

----------------------------------------

TITLE: Participant Property: participantInfo
DESCRIPTION: This property provides information about the participant. Changes to this information can be observed by utilizing the `io.livekit.android.util.flow` utility.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room.participant/-remote-participant/index

LANGUAGE: APIDOC
CODE:
```
@FlowObservable
@get:FlowObservable
var participantInfo: <Error class: unknown class>?
```

----------------------------------------

TITLE: RemoveParticipant API Endpoint
DESCRIPTION: Remove a participant from a room. Requires `roomAdmin`

SOURCE: https://docs.livekit.io/reference/server/server-apis

LANGUAGE: APIDOC
CODE:
```
RemoveParticipant
  room: string (Required) - name of the room
  identity: string (Required) - identity of the participant
```

----------------------------------------

TITLE: Handle LiveKit Remote Participant Connection
DESCRIPTION: This method is a callback triggered when a remote participant connects to the LiveKit room. It checks if a participant is already linked and, if not, attempts to link the newly connected participant using their identity.

SOURCE: https://docs.livekit.io/reference/python/livekit/agents/multimodal/index

LANGUAGE: python
CODE:
```
def _on_participant_connected(self, participant: rtc.RemoteParticipant):
    if self._linked_participant is None:
        return

    self._link_participant(participant.identity)
```

----------------------------------------

TITLE: Get Remote Participants
DESCRIPTION: Retrieves a dictionary of remote participants in the room, indexed by their identity.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/rtc/index

LANGUAGE: Python
CODE:
```
def remote_participants(self) -> Mapping[str, RemoteParticipant]:
    """Gets the remote participants in the room.

    Returns:
        dict[str, RemoteParticipant]: A dictionary of remote participants indexed by their
        identity.
    """
    return self._remote_participants
```

LANGUAGE: APIDOC
CODE:
```
remote_participants() -> Mapping[str, RemoteParticipant]
  Returns:
    dict[str, RemoteParticipant]: A dictionary of remote participants indexed by their identity.
```

----------------------------------------

TITLE: Update LiveKit Participant Track Subscriptions
DESCRIPTION: This function modifies a participant's track subscriptions within a LiveKit room, allowing for subscribing or unsubscribing from specific tracks. It requires administrator privileges for the room and returns an empty response object upon success.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: python
CODE:
```
async def update_subscriptions(
    self, update: UpdateSubscriptionsRequest
) -> UpdateSubscriptionsResponse:
    """Updates a participant's track subscriptions.

    Args:
        update (UpdateSubscriptionsRequest): arg containing:
            - room: str - Room name
            - identity: str - Participant identity
            - track_sids: list[str] - Track session IDs
            - subscribe: bool - True to subscribe, False to unsubscribe
            - participant_tracks: list[ParticipantTracks] - Participant track mappings

    Returns:
        UpdateSubscriptionsResponse: Empty response object
    """
    return await self._client.request(
        SVC,
        "UpdateSubscriptions",
        update,
        self._auth_header(VideoGrants(room_admin=True, room=update.room)),
        UpdateSubscriptionsResponse,
    )
```

LANGUAGE: APIDOC
CODE:
```
Method: update_subscriptions
Signature: async def update_subscriptions(self, update: room.UpdateSubscriptionsRequest) -> room.UpdateSubscriptionsResponse
Description: Updates a participant's track subscriptions.
Args:
  update (UpdateSubscriptionsRequest):
    - room: str - Room name
    - identity: str - Participant identity
    - track_sids: list[str] - Track session IDs
    - subscribe: bool - True to subscribe, False to unsubscribe
    - participant_tracks: list[ParticipantTracks] - Participant track mappings
Returns:
  UpdateSubscriptionsResponse: Empty response object
```

----------------------------------------

TITLE: Get Remote Participants Property (Python)
DESCRIPTION: Provides a mapping of remote participants currently in the room. The dictionary is indexed by participant identity, allowing easy access to individual remote participant objects.

SOURCE: https://docs.livekit.io/reference/python/livekit/rtc/room

LANGUAGE: Python
CODE:
```
@property
def remote_participants(self) -> Mapping[str, RemoteParticipant]:
    """Gets the remote participants in the room.

    Returns:
        dict[str, RemoteParticipant]: A dictionary of remote participants indexed by their
        identity.
    """
    return self._remote_participants
```

----------------------------------------

TITLE: LiveKit Room Service API Reference
DESCRIPTION: This snippet provides a structured overview of the LiveKit Room Service API, listing key classes like RoomService, Room, and various request/response models, along with their associated methods and properties. It serves as a quick reference for available API endpoints and data structures within the LiveKit room management system.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: APIDOC
CODE:
```
livekit.api.room_service.RemoveParticipantResponse:
  - DESCRIPTOR
livekit.api.room_service.Room:
  - DESCRIPTOR
livekit.api.room_service.RoomParticipantIdentity:
  - DESCRIPTOR
livekit.api.room_service.RoomService:
  - create_room
  - delete_room
  - forward_participant
  - get_participant
  - list_participants
  - list_rooms
  - mute_published_track
  - remove_participant
  - send_data
  - update_participant
  - update_room_metadata
  - update_subscriptions
livekit.api.room_service.SendDataRequest:
  - DESCRIPTOR
livekit.api.room_service.SendDataResponse:
  - DESCRIPTOR
livekit.api.room_service.UpdateParticipantRequest:
  - AttributesEntry
  - DESCRIPTOR
livekit.api.room_service.UpdateRoomMetadataRequest:
  - DESCRIPTOR
livekit.api.room_service.UpdateSubscriptionsRequest:
  - DESCRIPTOR
livekit.api.room_service.UpdateSubscriptionsResponse:
  - DESCRIPTOR
```

----------------------------------------

TITLE: LiveKit RTC Room API
DESCRIPTION: Documents the `Room` class in LiveKit RTC, which manages the connection and interactions within a LiveKit room. It provides methods for connecting, disconnecting, accessing participants, and handling events.

SOURCE: https://docs.livekit.io/reference/python/livekit/rtc/index

LANGUAGE: APIDOC
CODE:
```
Room:
  - connect()
  - connection_state
  - disconnect()
  - e2ee_manager
  - get_rtc_stats()
  - isconnected()
  - local_participant
  - metadata
  - name
  - on()
  - register_byte_stream_handler()
```

----------------------------------------

TITLE: Update LiveKit Room Participant Metadata
DESCRIPTION: Updates a participant's metadata or permissions within a LiveKit room.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: Python
CODE:
```
        async def update_participant(self, update: UpdateParticipantRequest) -> ParticipantInfo:
            """Updates a participant's metadata or permissions.

            Args:

```

LANGUAGE: APIDOC
CODE:
```
async def update_participant(
  update: room.UpdateParticipantRequest
) -> models.ParticipantInfo:
  Args:
```

----------------------------------------

TITLE: LiveKit Room RPC and Byte Stream Handler Registration (Python)
DESCRIPTION: This snippet demonstrates how to register RPC methods and byte stream handlers within a LiveKit room. It includes the setup for identifying the remote participant, a handler for clearing an audio buffer via RPC (ensuring the call originates from the expected participant), and a handler for receiving incoming byte streams, specifically for audio data, appending them to a list for subsequent processing.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/agents/voice/avatar/index

LANGUAGE: Python
CODE:
```
            self._remote_participant = await utils.wait_for_participant(
                room=self._room,
                identity=self._sender_identity,
                kind=rtc.ParticipantKind.PARTICIPANT_KIND_AGENT if not self._sender_identity else None,
            )

            def _handle_clear_buffer(data: rtc.RpcInvocationData) -> str:
                assert self._remote_participant is not None
                if data.caller_identity != self._remote_participant.identity:
                    logger.warning(
                        "clear buffer event received from unexpected participant",
                        extra={
                            "caller_identity": data.caller_identity,
                            "expected_identity": self._remote_participant.identity,
                        },
                    )
                    return "reject"

                if self._current_reader:
                    self._current_reader_cleared = True
                self.emit("clear_buffer")
                return "ok"

            self._room.local_participant.register_rpc_method(RPC_CLEAR_BUFFER, _handle_clear_buffer)

            def _handle_stream_received(
                reader: rtc.ByteStreamReader, remote_participant_id: str
            ) -> None:
                if (
                    not self._remote_participant
                    or remote_participant_id != self._remote_participant.identity
                ):
                    return

                self._stream_readers.append(reader)
                self._stream_reader_changed.set()

            self._room.register_byte_stream_handler(AUDIO_STREAM_TOPIC, _handle_stream_received)
```

----------------------------------------

TITLE: LiveKit Room remoteParticipants Property
DESCRIPTION: A read-only map of remote participants currently in the room, keyed by their unique identity. This property allows access to all remote participants connected to the room.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room/-room/index

LANGUAGE: Kotlin
CODE:
```
val remoteParticipants: Map<Participant.Identity, RemoteParticipant>
```

----------------------------------------

TITLE: Kotlin Example: Registering an RPC Method
DESCRIPTION: Illustrative Kotlin code snippet demonstrating how to use `room.localParticipant.registerRpcMethod` to set up a 'greet' RPC method. The example shows how to access `RpcInvocationData` parameters like `requestId`, `callerIdentity`, and `payload`, and how to return a string response from the handler.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room.participant/-local-participant/register-rpc-method

LANGUAGE: kotlin
CODE:
```
room.localParticipant.registerRpcMethod("greet") { (requestId, callerIdentity, payload, responseTimeout) ->
    Log.i("TAG", "Received greeting from ${callerIdentity}: ${payload}")

    // Return a string
    "Hello, ${callerIdentity}!"
}
```

----------------------------------------

TITLE: Link LiveKit Remote Participant
DESCRIPTION: This function attempts to link a remote participant to the agent using their identity. It retrieves the participant from the room's list and, if found, proceeds to subscribe to their microphone, logging an error if the identity is invalid.

SOURCE: https://docs.livekit.io/reference/python/livekit/agents/multimodal/index

LANGUAGE: python
CODE:
```
def _link_participant(self, participant_identity: str) -> None:
    self._linked_participant = self._room.remote_participants.get(
        participant_identity
    )
    if self._linked_participant is None:
        logger.error("_link_participant must be called with a valid identity")
        return

    self._subscribe_to_microphone()
```

----------------------------------------

TITLE: List LiveKit Room Participants
DESCRIPTION: Lists all active participants within a specified room. The method requires the room name as input and returns a response object containing a list of ParticipantInfo details for each participant.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: APIDOC
CODE:
```
list_participants(list: ListParticipantsRequest) -> ListParticipantsResponse
  Lists all participants in a room.
  Args:
    list (ListParticipantsRequest): arg containing:
      - room: str - Name of room to list participants from
  Returns:
    ListParticipantsResponse:
      - participants: list[ParticipantInfo] - List of participant details
```

LANGUAGE: python
CODE:
```
async def list_participants(self, list: ListParticipantsRequest) -> ListParticipantsResponse:
    return await self._client.request(
        SVC,
        "ListParticipants",
        list,
        self._auth_header(VideoGrants(room_admin=True, room=list.room)),
        ListParticipantsResponse,
    )
```

----------------------------------------

TITLE: LiveKit Android SDK: LocalParticipant Class Definition
DESCRIPTION: Defines the `LocalParticipant` class, a core component in the LiveKit Android SDK for managing a local user's participation in a room. It extends `Participant` and implements `OutgoingDataStreamManager` and `RpcManager` to handle data streams and RPC calls. The class also includes nested interfaces like `Factory` for instantiation and `PublishListener` for tracking publish events.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room.participant/-local-participant/index

LANGUAGE: APIDOC
CODE:
```
Class: LocalParticipant
  Package: io.livekit.android.room.participant
  Inherits:
    - Participant
    - OutgoingDataStreamManager
    - RpcManager

  Members:
    Types:
      Factory:
        Type: interface
        Annotations: @AssistedFactory
      PublishListener:
        Type: interface
```

----------------------------------------

TITLE: Remove LiveKit Participant from Room
DESCRIPTION: Removes a specific participant from a room, effectively disconnecting them. The method requires the room name and the identity of the participant to be removed. It returns an empty response object upon successful removal.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: APIDOC
CODE:
```
remove_participant(remove: RoomParticipantIdentity) -> RemoveParticipantResponse
  Removes a participant from a room.
  Args:
    remove (RoomParticipantIdentity): arg containing:
      - room: str - Room name
      - identity: str - Identity of participant to remove
  Returns:
    RemoveParticipantResponse: Empty response object
```

LANGUAGE: python
CODE:
```
async def remove_participant(
    self, remove: RoomParticipantIdentity
) -> RemoveParticipantResponse:
    return await self._client.request(
        SVC,
        "RemoveParticipant",
        remove,
        self._auth_header(VideoGrants(room_admin=True, room=remove.room)),
        RemoveParticipantResponse,
    )
```

----------------------------------------

TITLE: LiveKit Android Participant Class Properties API Reference
DESCRIPTION: Detailed API documentation for the public properties of the `Participant` class in the LiveKit Android SDK, including their types, descriptions, and Kotlin-specific annotations for observability and testing.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room.participant/-remote-participant/index

LANGUAGE: APIDOC
CODE:
```
Class: Participant (LiveKit Android SDK)

Properties:
- attributes:
    Type: Map<String, String>
    Access: var
    Description: The attributes set on this participant.
    Annotations: @FlowObservable, @get:FlowObservable, @set:VisibleForTesting
- audioLevel:
    Type: Float
    Access: var
    Description: Changes can be observed by using io.livekit.android.util.flow
    Annotations: @FlowObservable, @get:FlowObservable, @set:VisibleForTesting
- audioTrackPublications:
    Type: List<Pair<TrackPublication, Track?>>
    Access: val
    Description: Changes can be observed by using io.livekit.android.util.flow
    Annotations: @FlowObservable, @get:FlowObservable
- connectionQuality:
    Type: ConnectionQuality
    Access: var
    Description: Changes can be observed by using io.livekit.android.util.flow
    Annotations: @FlowObservable, @get:FlowObservable
- events:
    Type: EventListenable<ParticipantEvent>
    Access: val
    Description: No explicit description.
    Annotations: None
- hasInfo:
    Type: Boolean
    Access: val
    Description: No explicit description.
    Annotations: None
- identity:
    Type: Participant.Identity?
    Access: var
    Description: The participant's identity on the server. `name` should be preferred for UI usecases.
    Annotations: @FlowObservable, @get:FlowObservable, @set:VisibleForTesting
- isCameraEnabled:
    Type: Boolean
    Access: val
    Description: No explicit description.
    Annotations: @FlowObservable, @get:FlowObservable
- isMicrophoneEnabled:
    Type: Boolean
    Access: val
    Description: No explicit description.
    Annotations: @FlowObservable, @get:FlowObservable
- isScreenShareEnabled:
    Type: Boolean
    Access: val
    Description: No explicit description.
    Annotations: @FlowObservable, @get:FlowObservable
- isSpeaking:
    Type: Boolean
    Access: var
    Description: Changes can be observed by using io.livekit.android.util.flow
    Annotations: @FlowObservable, @get:FlowObservable, @set:VisibleForTesting
- joinedAt:
    Type: Any? (Error class: unknown class)
    Access: val
    Description: Timestamp when participant joined room, in milliseconds
    Annotations: None
- kind:
    Type: Participant.Kind
    Access: var
    Description: The kind of participant (i.e. a standard client participant, AI agent, etc.)
    Annotations: @FlowObservable, @get:FlowObservable
- lastSpokeAt:
    Type: (Not specified, inferred: Timestamp?)
    Access: (Not specified, inferred: val)
    Description: (Description not provided in snippet)
    Annotations: @FlowObservable, @get:FlowObservable
```

----------------------------------------

TITLE: Participant Property: videoTrackPublications
DESCRIPTION: A list of video track publications. Changes to this list can be observed by using the `io.livekit.android.util.flow` utility, allowing for reactive updates to video track states.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room.participant/-remote-participant/index

LANGUAGE: APIDOC
CODE:
```
val videoTrackPublications: List<Pair<TrackPublication, Track?>>
```

----------------------------------------

TITLE: LiveKit Participant Class API Reference
DESCRIPTION: Comprehensive API documentation for the Participant class, outlining its data members and callable methods. This class represents a participant in a LiveKit room, providing functionalities to manage their published tracks, monitor connection status, and handle permissions.

SOURCE: https://docs.livekit.io/reference/client-sdk-flutter/livekit_client/Participant-class

LANGUAGE: APIDOC
CODE:
```
Class: Participant
  Properties:
    trackPublications: Map<String, T>
      Description: Map of track sid => published track
      Attributes: final
    videoTracks: List<T>
      Attributes: read-only

  Methods:
    addListener(listener: VoidCallback): void
      Description: Register a closure to be called when the object changes.
      Attributes: inherited
    createListener({synchronized: bool = false}): EventsListener<ParticipantEvent>
      Attributes: inherited
    dispose(): Future<bool>
      Description: Discards any resources used by the object. After this is called, the object is not in a usable state and should be discarded (calls to addListener will throw after the object is disposed).
      Attributes: inherited
    getTrackPublicationBySource(source: TrackSource): T?
      Description: Tries to find a TrackPublication by its TrackSource. Otherwise, will return a compatible type of TrackPublication for the TrackSource specified. returns null when not found.
    isCameraEnabled(): bool
      Description: Convenience property to check whether TrackSource.camera is published or not.
    isMicrophoneEnabled(): bool
      Description: Convenience property to check whether TrackSource.microphone is published or not.
    isScreenShareEnabled(): bool
      Description: Convenience property to check whether TrackSource.screenShareVideo is published or not.
    noSuchMethod(invocation: Invocation): dynamic
      Description: Invoked when a nonexistent method or property is accessed.
      Attributes: inherited
    notifyListeners(): void
      Description: Call all the registered listeners.
      Attributes: inherited
    onDispose(func: OnDisposeFunc): void
      Attributes: inherited
    removeListener(listener: VoidCallback): void
      Description: Remove a previously registered closure from the list of closures that are notified when the object changes.
      Attributes: inherited
    setPermissions(newValue: ParticipantPermissions): ParticipantPermissions?
    toString(): String
      Description: A string representation of this object.
      Attributes: override
    unpublishAllTracks({notify: bool = true, stopOnUnpublish: bool?}): Future<void>
      Description: Convenience method to unpublish all tracks.
    unpublishTrack(trackSid: String, {notify: bool = true}): Future<void>
    updateConnectionQuality(quality: ConnectionQuality): void
    updateName(name: String): void
```

----------------------------------------

TITLE: LiveKit RTC LocalParticipant API
DESCRIPTION: Documents the `LocalParticipant` class in LiveKit RTC, which represents the current user in a room. It includes methods for managing participant attributes, metadata, track permissions, and data streaming.

SOURCE: https://docs.livekit.io/reference/python/livekit/rtc/index

LANGUAGE: APIDOC
CODE:
```
LocalParticipant:
  - set_attributes()
  - set_metadata()
  - set_name()
  - set_track_subscription_permissions()
  - stream_bytes()
  - stream_text()
  - unpublish_track()
  - unregister_rpc_method()
```

----------------------------------------

TITLE: Handle Participant Disconnection and Session Closure
DESCRIPTION: Manages the lifecycle of an agent session when a participant disconnects, ensuring proper session closure and room disconnection. It uses `asyncio.create_task` and `add_done_callback` for asynchronous cleanup.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/agents/index

LANGUAGE: Python
CODE:
```
def _on_closed(_: asyncio.Task[None]) -> None:
    self._close_session_atask = None

    if self._close_session_atask is not None:
        return

async def _close_session() -> None:
    if not self._agent_session._started:
        return

    logger.info(
        "closing agent session due to participant disconnect "
        "(disable via `RoomInputOptions.close_on_disconnect=False`)",
        extra={
            "participant": participant.identity,
            "reason": rtc.DisconnectReason.Name(
                participant.disconnect_reason or rtc.DisconnectReason.UNKNOWN_REASON
            ),
        },
    )
    await self._agent_session._aclose_impl(reason=CloseReason.PARTICIPANT_DISCONNECTED)
    await self._room.disconnect()

self._close_session_atask = asyncio.create_task(_close_session())
self._close_session_atask.add_done_callback(_on_closed)
```

----------------------------------------

TITLE: LiveKit Room Participant Connection Listener
DESCRIPTION: This partial snippet demonstrates setting up an event listener for 'participant_connected' events in a LiveKit room. The surrounding context implies this code is part of a function designed to return a participant matching a given identity, or the first participant if no identity is specified, potentially waiting for their connection.

SOURCE: https://docs.livekit.io/reference/python/livekit/agents/index

LANGUAGE: python
CODE:
```
self._room.on("participant_connected", _on_participant_connected)

            return await fut
```

----------------------------------------

TITLE: Perform an RPC Request to a Remote Participant
DESCRIPTION: This example shows how to initiate an RPC call to a remote participant using `room.localParticipant!.performRpc`. It specifies the `destinationIdentity`, `method` name, and `payload`. The call is asynchronous, and the snippet includes error handling for failed RPC requests, such as network issues or recipient errors.

SOURCE: https://docs.livekit.io/client-sdk-js

LANGUAGE: TypeScript
CODE:
```
try {
  const response = await room.localParticipant!.performRpc({
    destinationIdentity: 'recipient-identity',
    method: 'greet',
    payload: 'Hello from RPC!',
  });
  console.log('RPC response:', response);
} catch (error) {
  console.error('RPC call failed:', error);
}
```

----------------------------------------

TITLE: Get LiveKit Participant Details
DESCRIPTION: Retrieves detailed information about a specific participant within a room. This method requires both the room name and the participant's identity. It returns a comprehensive ParticipantInfo object.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: APIDOC
CODE:
```
get_participant(get: RoomParticipantIdentity) -> ParticipantInfo
  Gets details about a specific participant.
  Args:
    get (RoomParticipantIdentity): arg containing:
      - room: str - Room name
      - identity: str - Participant identity to look up
  Returns:
    ParticipantInfo:
      - sid: str - Participant session ID
      - identity: str - Participant identity
      - state: int - Connection state
      - tracks: list[TrackInfo] - Published tracks
      - metadata: str - Participant metadata
      - joined_at: int - Join timestamp
      - name: str - Display name
      - version: int - Protocol version
      - permission: ParticipantPermission - Granted permissions
      - region: str - Connected region
```

LANGUAGE: python
CODE:
```
async def get_participant(self, get: RoomParticipantIdentity) -> ParticipantInfo:
    return await self._client.request(
        SVC,
        "GetParticipant",
        get,
        self._auth_header(VideoGrants(room_admin=True, room=get.room)),
        ParticipantInfo,
    )
```

----------------------------------------

TITLE: Add SIP Participant to Room (Python)
DESCRIPTION: Adds a Session Initiation Protocol (SIP) participant to the LiveKit room. This function requires specifying the call destination, SIP trunk ID, participant identity, and an optional participant name. It handles the asynchronous task creation for integrating external SIP calls.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/agents/index

LANGUAGE: Python
CODE:
```
def add_sip_participant(
    self,
    *,
    call_to: str,
    trunk_id: str,
    participant_identity: str,
    participant_name: NotGivenOr[str] = "SIP-participant",
) -> asyncio.Future[api.SIPParticipantInfo]:  # type: ignore
    """
    Add a SIP participant to the room.

    Args:
        call_to: The number or SIP destination to transfer the participant to.
                     This can either be a number (+12345555555) or a
                     sip host (sip:<user>@<host>)
        trunk_id: The ID of the SIP trunk to use
        participant_identity: The identity of the participant to add
        participant_name: The name of the participant to add

    Make sure you have an outbound SIP trunk created in LiveKit.
    See https://docs.livekit.io/sip/trunk-outbound/ for more information.
    """
    task = asyncio.create_task(
        self.api.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                room_name=self._room.name,
                participant_identity=participant_identity,
                sip_trunk_id=trunk_id,
                sip_call_to=call_to,
                participant_name=participant_name if is_given(participant_name) else None,
            )
        ),
    )
    self._pending_tasks.append(task)
    task.add_done_callback(lambda _: self._pending_tasks.remove(task))
    return task
```

----------------------------------------

TITLE: API Definition for UpdateRoomMetadataRequest Class
DESCRIPTION: Defines the `UpdateRoomMetadataRequest` protocol message class, outlining its inheritance from Google Protobuf messages and its `DESCRIPTOR` class variable. This class handles requests to update room metadata.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: APIDOC
CODE:
```
class UpdateRoomMetadataRequest(*args, **kwargs):
  Description: A ProtocolMessage
  Ancestors:
    - google._upb._message.Message
    - google.protobuf.message.Message
  Class Variables:
    - var DESCRIPTOR
```

----------------------------------------

TITLE: Participant Property: permissions
DESCRIPTION: The permissions assigned to this participant. This property defines what actions the participant is authorized to perform within the LiveKit room.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room.participant/-remote-participant/index

LANGUAGE: APIDOC
CODE:
```
@FlowObservable
@get:FlowObservable
var permissions: ParticipantPermission?
```

----------------------------------------

TITLE: Python: Get Remote Participants in LiveKit Room
DESCRIPTION: Returns a dictionary of remote participants in the room, indexed by their identity.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/rtc/room

LANGUAGE: python
CODE:
```
@property
def remote_participants(self) -> Mapping[str, RemoteParticipant]:
    """Gets the remote participants in the room.

    Returns:
        dict[str, RemoteParticipant]: A dictionary of remote participants indexed by their
        identity.
    """
    return self._remote_participants
```

----------------------------------------

TITLE: Update LiveKit Participant Information
DESCRIPTION: This function updates a participant's metadata, permissions, or display name within a LiveKit room. It requires administrator privileges for the room and returns the updated participant information.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: python
CODE:
```
async def update_participant(self, update: room.UpdateParticipantRequest) -> models.ParticipantInfo:
    """
    update (UpdateParticipantRequest): arg containing:
        - room: str - Room name
        - identity: str - Participant identity
        - metadata: str - New metadata
        - permission: ParticipantPermission - New permissions
        - name: str - New display name
        - attributes: dict[str, str] - Key-value attributes

    Returns:
        ParticipantInfo: Updated participant information
    """
    return await self._client.request(
        SVC,
        "UpdateParticipant",
        update,
        self._auth_header(VideoGrants(room_admin=True, room=update.room)),
        ParticipantInfo,
    )
```

LANGUAGE: APIDOC
CODE:
```
Method: update_participant
Signature: async def update_participant(self, update: room.UpdateParticipantRequest) -> models.ParticipantInfo
Description: Updates a participant's metadata or permissions.
Args:
  update (UpdateParticipantRequest):
    - room: str - Room name
    - identity: str - Participant identity
    - metadata: str - New metadata
    - permission: ParticipantPermission - New permissions
    - name: str - New display name
    - attributes: dict[str, str] - Key-value attributes
Returns:
  ParticipantInfo: Updated participant information
```

----------------------------------------

TITLE: LiveKit Server API: Updating Participant Attributes and Metadata
DESCRIPTION: This example illustrates how to update participant attributes and metadata from a server application using the LiveKit `RoomServiceClient`. It utilizes the `updateParticipant` method, specifying the room, identity, and the new attributes or metadata to apply. This allows server-side control over participant data.

SOURCE: https://docs.livekit.io/home/client/data/participant-attributes

LANGUAGE: nodejs
CODE:
```
import { RoomServiceClient } from 'livekit-server-sdk';
const roomServiceClient = new RoomServiceClient('myhost', 'api-key', 'my secret');
roomServiceClient.updateParticipant('room', 'identity', {
attributes: {
myKey: 'myValue',
},
metadata: 'updated metadata',
});
```

----------------------------------------

TITLE: LiveKit React State Management Hooks Reference
DESCRIPTION: A list of recommended LiveKit React hooks for accessing and managing the current state of a room, participants, and tracks. These hooks provide robust state handling for lower-level features.

SOURCE: https://docs.livekit.io/reference/components/react/guide

LANGUAGE: APIDOC
CODE:
```
useParticipants
useTracks
```

----------------------------------------

TITLE: Define LiveKit RemoteParticipant Class
DESCRIPTION: Defines the `RemoteParticipant` class, which represents a participant in a LiveKit room that is not local. It inherits from `Participant`, initializes with `OwnedParticipant` info, and manages a dictionary of `RemoteTrackPublication` objects.

SOURCE: https://docs.livekit.io/reference/python/livekit/rtc/participant

LANGUAGE: python
CODE:
```
class RemoteParticipant(Participant):
    def __init__(self, owned_info: proto_participant.OwnedParticipant) -> None:
        super().__init__(owned_info)
        self._track_publications: dict[str, RemoteTrackPublication] = {}  # type: ignore

    @property
    def track_publications(self) -> Mapping[str, RemoteTrackPublication]:
        """
A dictionary of track publications associated with the participant.
"""
        return self._track_publications

    def __repr__(self) -> str:
```

----------------------------------------

TITLE: LiveKit Android SDK ParticipantConnected Event - Participant Property Definition
DESCRIPTION: Defines the `participant` property, a read-only value, available within the `ParticipantConnected` event. This property provides access to the `RemoteParticipant` object that has just connected to the room, allowing developers to interact with the newly joined participant.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.events/-room-event/-participant-connected/participant

LANGUAGE: Kotlin
CODE:
```
val participant: RemoteParticipant
```

----------------------------------------

TITLE: Manage Participant Entrypoint Tasks
DESCRIPTION: This Python snippet demonstrates how `JobContext` manages participant entrypoints, creating and tracking asynchronous tasks for each participant. It includes logic to prevent duplicate tasks and handle cases where a participant rejoins before a previous task completes.

SOURCE: https://docs.livekit.io/reference/python/livekit/agents/index

LANGUAGE: python
CODE:
```
            for coro, kind in self._participant_entrypoints:
                if isinstance(kind, list):
                    if p.kind not in kind:
                        continue
                else:
                    if p.kind != kind:
                        continue

                if (p.identity, coro) in self._participant_tasks:
                    logger.warning(
                        f"a participant has joined before a prior participant task matching the same identity has finished: '{p.identity}'"
                    )
                task_name = f"part-entry-{p.identity}-{coro.__name__}"
                task = asyncio.create_task(coro(self, p), name=task_name)
                self._participant_tasks[(p.identity, coro)] = task
                task.add_done_callback(
                    lambda _: self._participant_tasks.pop((p.identity, coro))
                )
```

----------------------------------------

TITLE: Access and Attach Remote Participant Tracks
DESCRIPTION: Illustrates how to retrieve a `RemoteParticipant` by identity and attach their enabled camera track to an HTML video element. It checks if the track is subscribed before attempting to attach.

SOURCE: https://docs.livekit.io/reference/client-sdk-js

LANGUAGE: JavaScript
CODE:
```
// get a RemoteParticipant by their identity
const p = room.remoteParticipants.get('participant-identity');
if (p) {
  // if the other user has enabled their camera, attach it to a new HTMLVideoElement
  if (p.isCameraEnabled) {
    const publication = p.getTrackPublication(Track.Source.Camera);
    if (publication?.isSubscribed) {
      const videoElement = publication.videoTrack?.attach();
      // do something with the element
    }
  }
}
```

----------------------------------------

TITLE: LiveKit Agent Job Simulation Function
DESCRIPTION: This asynchronous Python function simulates a job within the LiveKit environment. It creates a new room, optionally retrieves a participant, and then constructs and queues a `WorkerMessage` to initiate the job simulation. It relies on the LiveKit API client for room and participant management.

SOURCE: https://docs.livekit.io/reference/python/livekit/agents/index

LANGUAGE: python
CODE:
```
        async def simulate_job(
            self, room: str, participant_identity: str | None = None
        ) -> None:
            assert self._api is not None

            room_obj = await self._api.room.create_room(api.CreateRoomRequest(name=room))
            participant = None
            if participant_identity:
                participant = await self._api.room.get_participant(
                    api.RoomParticipantIdentity(room=room, identity=participant_identity)
                )

            msg = agent.WorkerMessage()
            msg.simulate_job.room.CopyFrom(room_obj)
            if participant:
                msg.simulate_job.participant.CopyFrom(participant)

            await self._queue_msg(msg)
```

----------------------------------------

TITLE: Mute or Unmute LiveKit Room Track
DESCRIPTION: Mutes or unmutes a participant's published track in a LiveKit room. This operation requires room admin privileges.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: Python
CODE:
```
            update: MuteRoomTrackRequest,
        ) -> MuteRoomTrackResponse:
            """Mutes or unmutes a participant's published track.

            Args:
                update (MuteRoomTrackRequest): arg containing:
                    - room: str - Room name
                    - identity: str - Participant identity
                    - track_sid: str - Track session ID to mute
                    - muted: bool - True to mute, False to unmute

            Returns:
                MuteRoomTrackResponse containing:
                    - track: TrackInfo - Updated track information
            """
            return await self._client.request(
                SVC,
                "MutePublishedTrack",
                update,
                self._auth_header(VideoGrants(room_admin=True, room=update.room)),
                MuteRoomTrackResponse,
            )
```

LANGUAGE: APIDOC
CODE:
```
async def mute_published_track(
  update: MuteRoomTrackRequest
) -> MuteRoomTrackResponse:
  Args:
    update (MuteRoomTrackRequest):
      room: str - Room name
      identity: str - Participant identity
      track_sid: str - Track session ID to mute
      muted: bool - True to mute, False to unmute
  Returns:
    MuteRoomTrackResponse:
      track: TrackInfo - Updated track information
```

----------------------------------------

TITLE: Participant Property: lastSpokeAt
DESCRIPTION: Timestamp when the participant last started speaking, in milliseconds. This property indicates the most recent time a participant was detected as actively speaking.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room.participant/-remote-participant/index

LANGUAGE: APIDOC
CODE:
```
var lastSpokeAt: Long?
```

----------------------------------------

TITLE: Delete LiveKit Room
DESCRIPTION: Deletes a specified LiveKit room and disconnects all participants. This method uses the LiveKit API client for the request.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: python
CODE:
```
async def delete_room(self, delete: DeleteRoomRequest) -> DeleteRoomResponse:
    """Deletes a room and disconnects all participants.

    Args:
        delete (DeleteRoomRequest): arg containing:
            - room: str - Name of room to delete

    Returns:
        DeleteRoomResponse: Empty response object
    """
    return await self._client.request(
        SVC,
        "DeleteRoom",
        delete,
        self._auth_header(VideoGrants(room_create=True)),
        DeleteRoomResponse,
    )
```

----------------------------------------

TITLE: Get Local Participant Property (Python)
DESCRIPTION: Accesses the local participant object within the room. This property returns an instance of `LocalParticipant`, allowing interaction with the current user's presence and media.

SOURCE: https://docs.livekit.io/reference/python/livekit/rtc/room

LANGUAGE: Python
CODE:
```
@property
def local_participant(self) -> LocalParticipant:
    """Gets the local participant in the room.

    Returns:
        LocalParticipant: The local participant in the room.
    """
    if self._local_participant is None:
        raise Exception("cannot access local participant before connecting")

    return self._local_participant
```

----------------------------------------

TITLE: Handle LiveKit Participant Connected Event in Python
DESCRIPTION: Demonstrates how to register a callback function to handle the "participant_connected" event emitted by a LiveKit Room object in Python.

SOURCE: https://docs.livekit.io/reference/python/livekit/rtc/index

LANGUAGE: Python
CODE:
```
def on_participant_connected(participant):
    print(f"Participant connected: {participant.identity}")

room.on("participant_connected", on_participant_connected)
```

----------------------------------------

TITLE: Room.remote_participants Property (APIDOC)
DESCRIPTION: API documentation for the `remote_participants` property, which returns a dictionary of remote participants.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/rtc/index

LANGUAGE: APIDOC
CODE:
```
prop remote_participants : Mapping[str, RemoteParticipant]
  Gets the remote participants in the room.
  Returns:
    dict[str, RemoteParticipant]: A dictionary of remote participants indexed by their identity.
```

----------------------------------------

TITLE: API Definition for UpdateParticipantRequest Class
DESCRIPTION: Defines the `UpdateParticipantRequest` protocol message class, detailing its inheritance and specific class variables, including `AttributesEntry`. This class is used for updating participant information.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: APIDOC
CODE:
```
class UpdateParticipantRequest(*args, **kwargs):
  Description: A ProtocolMessage
  Ancestors:
    - google._upb._message.Message
    - google.protobuf.message.Message
  Class Variables:
    - var AttributesEntry: A ProtocolMessage
    - var DESCRIPTOR
```

----------------------------------------

TITLE: Register an RPC Method for Inter-Participant Communication
DESCRIPTION: This snippet demonstrates how a local participant can register a custom RPC method using `room.localParticipant?.registerRpcMethod`. It requires a method name and an asynchronous handler function that processes incoming RPC invocations, providing access to caller identity and payload. The handler can return a response string.

SOURCE: https://docs.livekit.io/client-sdk-js

LANGUAGE: TypeScript
CODE:
```
room.localParticipant?.registerRpcMethod(
  // method name - can be any string that makes sense for your application
  'greet',

  // method handler - will be called when the method is invoked by a RemoteParticipant
  async (data: RpcInvocationData) => {
    console.log(`Received greeting from ${data.callerIdentity}: ${data.payload}`);
    return `Hello, ${data.callerIdentity}!`;
  },
);
```

----------------------------------------

TITLE: LiveKit Room Service API: Forward Participant
DESCRIPTION: Documents the `ForwardParticipant` method for moving a participant and their tracks between rooms, along with its Python implementation. This feature is exclusive to LiveKit Cloud/Private Cloud.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: APIDOC
CODE:
```
ForwardParticipant(forward: ForwardParticipantRequest)
  Description: Forwards a participant and their published tracks from one room to another.
  Availability: This feature is only available for LiveKit Cloud/Private Cloud.
  Parameters:
    forward (ForwardParticipantRequest):
      - room: str - Room name
      - identity: str - identity of Participant to forward
      - destination_room: str - Destination room name
  Returns: None (currently nothing is returned)
```

LANGUAGE: python
CODE:
```
await self._client.request(
    SVC,
    "ForwardParticipant",
    forward,
    self._auth_header(VideoGrants(room_admin=True, room=forward.room)),
    ForwardParticipantResponse,
)
```

----------------------------------------

TITLE: Forward LiveKit Participant
DESCRIPTION: Forwards a participant and their published tracks from one room to another. This feature is specific to LiveKit Cloud/Private Cloud deployments.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: python
CODE:
```
async def forward_participant(self, forward: ForwardParticipantRequest) -> None:
    """Forwards a participant and their published tracks from one room to another.

    This feature is only available for LiveKit Cloud/Private Cloud.

    Args:
        forward (ForwardParticipantRequest): arg containing:
            - room: str - Room name
            - identity: str - identity of Participant to forward
            - destination_room: str - Destination room name
    """
    # currently nothing is returned
    await self._client.request(
        SVC,
        "ForwardParticipant",
        forward,
        self._auth_header(VideoGrants(room_admin=True, room=forward.room)),
        ForwardParticipantResponse,
    )
```

----------------------------------------

TITLE: LiveKit Participant Class Properties Reference
DESCRIPTION: Detailed documentation for the properties available on the `Participant` class within the LiveKit client library, including their types, descriptions, and access modifiers. This covers attributes related to audio, video, connection status, identity, and more.

SOURCE: https://docs.livekit.io/reference/client-sdk-flutter/livekit_client/RemoteParticipant-class

LANGUAGE: APIDOC
CODE:
```
audioLevel: double
  Description: Audio level between 0-1, 1 being the loudest.
  Access: read / write, inherited
audioTracks: List<RemoteTrackPublication<RemoteAudioTrack>>
  Description: A convenience property to get all audio tracks.
  Access: read-only, override
connectionQuality: ConnectionQuality
  Description: Connection quality between the Participant and the Server.
  Access: read-only, inherited
disposeFuncCount: int
  Description: No specific description provided.
  Access: read-only, inherited
events: EventsEmitter<ParticipantEvent>
  Description: No specific description provided.
  Access: final, inherited
firstTrackEncryptionType: EncryptionType
  Description: No specific description provided.
  Access: read-only, inherited
hasAudio: bool
  Description: true if this Participant has more than 1 AudioTrack.
  Access: read-only, inherited
hashCode: int
  Description: (Equality operator) Participant.hashCode is same as `sid.hashCode`.
  Access: read-only, inherited
hasInfo: bool
  Description: No specific description provided.
  Access: read-only, inherited
hasListeners: bool
  Description: Whether any listeners are currently registered.
  Access: read-only, inherited
hasVideo: bool
  Description: true if this Participant has more than 1 VideoTrack.
  Access: read-only, inherited
identity: String
  Description: User-assigned identity.
  Access: read / write, inherited
isDisposed: bool
  Description: No specific description provided.
  Access: read-only, inherited
isEncrypted: bool
  Description: No specific description provided.
  Access: read-only, inherited
isMuted: bool
  Description: true if Participant is publishing an AudioTrack and is muted.
  Access: read-only, inherited
isSpeaking: bool
  Description: if Participant is currently speaking.
  Access: read-only, inherited
joinedAt: DateTime
  Description: when the participant joined the room.
  Access: read-only, inherited
lastSpokeAt: DateTime?
  Description: When the participant had last spoken.
  Access: read / write, inherited
metadata: String?
  Description: Client-assigned metadata, opaque to livekit.
  Access: read / write, inherited
name: String
  Description: Name of the participant (readonly).
  Access: read-only, inherited
permissions: ParticipantPermissions
  Description: No specific description provided.
  Access: read-only, inherited
room: Room
  Description: Reference to Room.
  Access: final, inherited
runtimeType: Type
  Description: A representation of the runtime type of the object.
  Access: read-only, inherited
```

----------------------------------------

TITLE: Get E2EE Manager for Room
DESCRIPTION: Retrieves the end-to-end encryption (E2EE) manager instance associated with the room. This manager provides functionalities for handling E2EE within the LiveKit room.

SOURCE: https://docs.livekit.io/reference/python/livekit/rtc/room

LANGUAGE: APIDOC
CODE:
```
E2EEManager:
  description: The E2EE manager instance.
  returns: E2EEManager
```

----------------------------------------

TITLE: Manage LiveKit Track Subscriptions via Server API (Node.js)
DESCRIPTION: Illustrates how to use the LiveKit `RoomServiceClient` in Node.js to programmatically update track subscriptions for a specific participant in a room. It shows examples for both subscribing to and unsubscribing from tracks.

SOURCE: https://docs.livekit.io/home/client/tracks/subscribe

LANGUAGE: Node.js
CODE:
```
import { RoomServiceClient } from 'livekit-server-sdk';

const roomServiceClient = new RoomServiceClient('myhost', 'api-key', 'my secret');

// Subscribe to new track
roomServiceClient.updateSubscriptions('myroom', 'receiving-participant-identity', ['TR_TRACKID'], true);

// Unsubscribe from existing track
roomServiceClient.updateSubscriptions('myroom', 'receiving-participant-identity', ['TR_TRACKID'], false);
```

----------------------------------------

TITLE: Update LiveKit Participant Permissions
DESCRIPTION: This snippet demonstrates how to dynamically modify a participant's permissions within a LiveKit room using the `UpdateParticipant` method. It provides examples of promoting an audience member to a speaker role and then reverting them, highlighting how changes to `CanPublish` automatically affect track publication.

SOURCE: https://docs.livekit.io/home/server/managing-participants

LANGUAGE: Go
CODE:
```
// Promotes an audience member to a speaker
res, err := c.UpdateParticipant(context.Background(), &livekit.UpdateParticipantRequest{
	Room: roomName,
	Identity: identity,
	Permission: &livekit.ParticipantPermission{
		CanSubscribe: true,
		CanPublish: true,
		CanPublishData: true,
	},
})
// ...and later move them back to audience
res, err := c.UpdateParticipant(context.Background(), &livekit.UpdateParticipantRequest{
	Room: roomName,
	Identity: identity,
	Permission: &livekit.ParticipantPermission{
		CanSubscribe: true,
		CanPublish: false,
		CanPublishData: true,
	},
})
```

----------------------------------------

TITLE: LiveKit SDK: Receiving and Updating Participant Attributes/Metadata
DESCRIPTION: This snippet demonstrates how LiveKit SDKs handle participant attribute and metadata changes. It shows how to subscribe to `RoomEvent.ParticipantAttributesChanged` and `RoomEvent.ParticipantMetadataChanged` events to receive updates, and how to use `room.localParticipant.setAttributes()` and `room.localParticipant.setMetadata()` to update the local participant's information. Updating requires the `canUpdateOwnMetadata` permission.

SOURCE: https://docs.livekit.io/home/client/state/participant-attributes

LANGUAGE: JavaScript
CODE:
```
// receiving changes
room.on(
RoomEvent.ParticipantAttributesChanged,
(changed: Record<string, string>, participant: Participant) => {
console.log(
'participant attributes changed',
changed,
'all attributes',
participant.attributes,
);
},
);
room.on(
RoomEvent.ParticipantMetadataChanged,
(oldMetadata: string | undefined, participant: Participant) => {
console.log('metadata changed from', oldMetadata, participant.metadata);
},
);
// updating local participant
room.localParticipant.setAttributes({
myKey: 'myValue',
myOtherKey: 'otherValue',
});
room.localParticipant.setMetadata(
JSON.stringify({
some: 'values',
}),
);
```

----------------------------------------

TITLE: Get Participant by Identity
DESCRIPTION: This method allows retrieving a participant object from the room by their unique identity string. It returns the `Participant` object if found, otherwise undefined.

SOURCE: https://docs.livekit.io/reference/client-sdk-js/classes/Room

LANGUAGE: APIDOC
CODE:
```
getParticipantByIdentity(identity: string): undefined | Participant
  Parameters:
    identity: string
  Returns: undefined | Participant
```

----------------------------------------

TITLE: LiveKit Room Service API: Update Subscriptions
DESCRIPTION: Documents the `update_subscriptions` method for managing a participant's track subscriptions, including subscribing or unsubscribing from specific tracks, along with its Python usage.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: APIDOC
CODE:
```
update_subscriptions(update: UpdateSubscriptionsRequest) -> UpdateSubscriptionsResponse
  Description: Updates a participant's track subscriptions.
  Parameters:
    update (UpdateSubscriptionsRequest):
      - room: str - Room name
      - identity: str - Participant identity
      - track_sids: list[str] - Track session IDs
      - subscribe: bool - True to subscribe, False to unsubscribe
      - participant_tracks: list[ParticipantTracks] - Participant track mappings
  Returns:
    UpdateSubscriptionsResponse: Empty response object
```

LANGUAGE: python
CODE:
```
return await self._client.request(
    SVC,
    "UpdateSubscriptions",
    update,
    self._auth_header(VideoGrants(room_admin=True, room=update.room)),
    UpdateSubscriptionsResponse,
)
```

----------------------------------------

TITLE: LiveKit Room Connection Example
DESCRIPTION: Provides a practical example of how to connect to a LiveKit room using the `Room` class. It demonstrates setting up an event listener for participant connections before initiating the room connection with a specified WebSocket URL and authentication token.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/rtc/index

LANGUAGE: python
CODE:
```
room = Room()

# Listen for events before connecting to the room
@room.on("participant_connected")
def on_participant_connected(participant):
    print(f"Participant connected: {participant.identity}")

await room.connect("ws://localhost:7880", "your_token")
```

----------------------------------------

TITLE: RemoteParticipant Class Definition
DESCRIPTION: Represents a remote participant in a LiveKit room, inheriting from the `Participant` base class. It manages a dictionary of `RemoteTrackPublication` objects for tracks published by the remote participant, allowing access to their published media.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/rtc/participant

LANGUAGE: python
CODE:
```
class RemoteParticipant(Participant):
    def __init__(self, owned_info: proto_participant.OwnedParticipant) -> None:
        super().__init__(owned_info)
        self._track_publications: dict[str, RemoteTrackPublication] = {}  # type: ignore

    @property
    def track_publications(self) -> Mapping[str, RemoteTrackPublication]:
        """
        A dictionary of track publications associated with the participant.
        """
        return self._track_publications

    def __repr__(self) -> str:
```

----------------------------------------

TITLE: Delete LiveKit Room
DESCRIPTION: Deletes a specified room and disconnects all participants currently in it. The method requires the name of the room to be deleted and returns an empty response object upon successful deletion.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: APIDOC
CODE:
```
delete_room(delete: DeleteRoomRequest) -> DeleteRoomResponse
  Deletes a room and disconnects all participants.
  Args:
    delete (DeleteRoomRequest): arg containing:
      - room: str - Name of room to delete
  Returns:
    DeleteRoomResponse: Empty response object
```

LANGUAGE: python
CODE:
```
async def delete_room(self, delete: DeleteRoomRequest) -> DeleteRoomResponse:
    return await self._client.request(
        SVC,
        "DeleteRoom",
        delete,
        self._auth_header(VideoGrants(room_create=True)),
        DeleteRoomResponse,
    )
```

----------------------------------------

TITLE: Handle Participant Connection and Human Input Initialization
DESCRIPTION: These methods manage the connection of a remote participant and initialize the `HumanInput` component. `_on_participant_connected` acts as an entry point, while `_link_participant` performs the actual setup, associating VAD, STT, and other services with the participant.

SOURCE: https://docs.livekit.io/reference/python/livekit/agents/pipeline/pipeline_agent

LANGUAGE: Python
CODE:
```
def _on_participant_connected(self, participant: rtc.RemoteParticipant):
    if self._human_input is not None:
        return

    self._link_participant(participant.identity)

def _link_participant(self, identity: str) -> None:
    participant = self._room.remote_participants.get(identity)
    if participant is None:
        logger.error("_link_participant must be called with a valid identity")
        return

    self._human_input = HumanInput(
        room=self._room,
        vad=self._vad,
        stt=self._stt,
        participant=participant,
        transcription=self._opts.transcription.user_transcription,
        noise_cancellation=self._noise_cancellation,
    )
```

----------------------------------------

TITLE: Process LiveKit Room Events
DESCRIPTION: This comprehensive method dispatches various LiveKit room events based on their type. It handles participant connections and disconnections, manages the lifecycle of local and remote tracks (publishing, unpublishing, subscribing, unsubscribing), and updates the state of participants and track publications accordingly. It emits corresponding events for external listeners.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/rtc/index

LANGUAGE: Python
CODE:
```
        def _on_room_event(self, event: proto_room.RoomEvent):
            which = event.WhichOneof("message")
            if which == "participant_connected":
                rparticipant = self._create_remote_participant(event.participant_connected.info)
                self.emit("participant_connected", rparticipant)
            elif which == "participant_disconnected":
                identity = event.participant_disconnected.participant_identity
                rparticipant = self._remote_participants.pop(identity)
                rparticipant._info.disconnect_reason = event.participant_disconnected.disconnect_reason
                self.emit("participant_disconnected", rparticipant)
            elif which == "local_track_published":
                sid = event.local_track_published.track_sid
                lpublication = self.local_participant.track_publications[sid]
                ltrack = lpublication.track
                self.emit("local_track_published", lpublication, ltrack)
            elif which == "local_track_unpublished":
                sid = event.local_track_unpublished.publication_sid
                lpublication = self.local_participant.track_publications[sid]
                self.emit("local_track_unpublished", lpublication)
            elif which == "local_track_subscribed":
                sid = event.local_track_subscribed.track_sid
                lpublication = self.local_participant.track_publications[sid]
                lpublication._first_subscription.set_result(None)
                self.emit("local_track_subscribed", lpublication.track)
            elif which == "track_published":
                rparticipant = self._remote_participants[event.track_published.participant_identity]
                rpublication = RemoteTrackPublication(event.track_published.publication)
                rparticipant._track_publications[rpublication.sid] = rpublication
                self.emit("track_published", rpublication, rparticipant)
            elif which == "track_unpublished":
                rparticipant = self._remote_participants[event.track_unpublished.participant_identity]
                rpublication = rparticipant._track_publications.pop(
                    event.track_unpublished.publication_sid
                )
                self.emit("track_unpublished", rpublication, rparticipant)
            elif which == "track_subscribed":
                owned_track_info = event.track_subscribed.track
                track_info = owned_track_info.info
                rparticipant = self._remote_participants[event.track_subscribed.participant_identity]
                rpublication = rparticipant.track_publications[track_info.sid]
                rpublication._subscribed = True
                if track_info.kind == TrackKind.KIND_VIDEO:
                    remote_video_track = RemoteVideoTrack(owned_track_info)
                    rpublication._track = remote_video_track
                    self.emit("track_subscribed", remote_video_track, rpublication, rparticipant)
                elif track_info.kind == TrackKind.KIND_AUDIO:
                    remote_audio_track = RemoteAudioTrack(owned_track_info)
                    rpublication._track = remote_audio_track
                    self.emit("track_subscribed", remote_audio_track, rpublication, rparticipant)
            elif which == "track_unsubscribed":
                identity = event.track_unsubscribed.participant_identity
                rparticipant = self._remote_participants[identity]
                rpublication = rparticipant.track_publications[event.track_unsubscribed.track_sid]
                rtrack = rpublication.track
                rpublication._track = None
                rpublication._subscribed = False
                self.emit("track_unsubscribed", rtrack, rpublication, rparticipant)
```

----------------------------------------

TITLE: Python Function: Link to Remote Participant
DESCRIPTION: Links the agent to a specific remote participant by their identity. It retrieves the participant from the room's list and, if found, proceeds to subscribe to their microphone, logging an error if the identity is invalid.

SOURCE: https://docs.livekit.io/reference/python/livekit/agents/multimodal/multimodal_agent

LANGUAGE: python
CODE:
```
def _link_participant(self, participant_identity: str) -> None:
    self._linked_participant = self._room.remote_participants.get(
        participant_identity
    )
    if self._linked_participant is None:
        logger.error("_link_participant must be called with a valid identity")
        return

    self._subscribe_to_microphone()
```

----------------------------------------

TITLE: Access and Attach Remote Participant Camera Track
DESCRIPTION: Illustrates how to retrieve a `RemoteParticipant` by their identity and conditionally attach their camera track to a new HTMLVideoElement if the camera is enabled and the track is subscribed.

SOURCE: https://docs.livekit.io/reference/client-sdk-js/index

LANGUAGE: javascript
CODE:
```
// get a RemoteParticipant by their identity
const p = room.remoteParticipants.get('participant-identity');
if (p) {
  // if the other user has enabled their camera, attach it to a new HTMLVideoElement
  if (p.isCameraEnabled) {
    const publication = p.getTrackPublication(Track.Source.Camera);
    if (publication?.isSubscribed) {
      const videoElement = publication.videoTrack?.attach();
      // do something with the element
    }
  }
}
```

----------------------------------------

TITLE: LiveKit RoomService Python Client Implementation
DESCRIPTION: Full Python implementation of the `RoomService` client for LiveKit API, including initialization and the `create_room` method. This class provides an interface for managing LiveKit rooms and participants.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: python
CODE:
```
class RoomService(Service):
    """Client for LiveKit RoomService API

    Recommended way to use this service is via `livekit.api.LiveKitAPI`:

    ```python
    from livekit import api
    lkapi = api.LiveKitAPI()
    room_service = lkapi.room
    ```

    Also see https://docs.livekit.io/home/server/managing-rooms/ and https://docs.livekit.io/home/server/managing-participants/
    """

    def __init__(self, session: aiohttp.ClientSession, url: str, api_key: str, api_secret: str):
        super().__init__(session, url, api_key, api_secret)

    async def create_room(
        self,
        create: CreateRoomRequest,
    ) -> Room:
        """Creates a new room with specified configuration.

        Args:
            create (CreateRoomRequest): arg containing:
                - name: str - Unique room name
                - empty_timeout: int - Seconds to keep room open if empty
                - max_participants: int - Max allowed participants
                - metadata: str - Custom room metadata
                - egress: RoomEgress - Egress configuration
                - min_playout_delay: int - Minimum playout delay in ms
                - max_playout_delay: int - Maximum playout delay in ms
                - sync_streams: bool - Enable A/V sync for playout delays >200ms

        Returns:
            Room: The created room object
        """
        return await self._client.request(
            SVC,
            "CreateRoom",
            create,
        )
```

----------------------------------------

TITLE: LiveKit Android SDK: RpcInvocationData.callerIdentity Property Definition
DESCRIPTION: Documents the `callerIdentity` property of the `RpcInvocationData` class, which represents the identity of the remote participant who initiated an RPC call. This property is of type `Participant.Identity`.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room.participant/-rpc-invocation-data/caller-identity

LANGUAGE: APIDOC
CODE:
```
Class: RpcInvocationData
  Property: callerIdentity
    Type: Participant.Identity
    Description: The identity of the RemoteParticipant who initiated the RPC call
```

----------------------------------------

TITLE: Get Room E2EE Manager (Python)
DESCRIPTION: Accesses the End-to-End Encryption (E2EE) manager instance associated with the LiveKit room. This manager handles encryption-related operations.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/rtc/index

LANGUAGE: Python
CODE:
```
@property
def e2ee_manager(self) -> E2EEManager:
    """Gets the end-to-end encryption (E2EE) manager for the room.

    Returns:
        E2EEManager: The E2EE manager instance.
    """
    return self._e2ee_manager
```

----------------------------------------

TITLE: Accessing LiveKit Participant and Stream Properties (Python)
DESCRIPTION: Provides methods and properties to retrieve the current video input, linked remote participant, and audio output subscription status within a LiveKit room. These properties offer convenient access to the state of associated streams and participants.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/agents/index

LANGUAGE: Python
CODE:
```
        def video_input(self) -> VideoInput | None:
            return self._video_input

        @property
        def linked_participant(self) -> rtc.RemoteParticipant | None:
            if not self._participant_available_fut.done():
                return None
            return self._participant_available_fut.result()

        @property
        def subscribed_fut(self) -> asyncio.Future[None] | None:
            if self._audio_output:
                return self._audio_output.subscribed
            return None
```

----------------------------------------

TITLE: Python: Implement Cartesia ChunkedStream for TTS
DESCRIPTION: This Python class, `ChunkedStream`, extends `tts.ChunkedStream` to handle chunked text synthesis via Cartesia's bytes endpoint. It manages HTTP requests, authentication, audio streaming, and error handling for real-time text-to-speech.

SOURCE: https://docs.livekit.io/reference/python/livekit/plugins/cartesia/index

LANGUAGE: python
CODE:
```
class ChunkedStream(tts.ChunkedStream):
    """Synthesize chunked text using the bytes endpoint"""

    def __init__(
        self,
        *,
        tts: TTS,
        input_text: str,
        opts: _TTSOptions,
        session: aiohttp.ClientSession,
        conn_options: Optional[APIConnectOptions] = None,
    ) -> None:
        super().__init__(tts=tts, input_text=input_text, conn_options=conn_options)
        self._opts, self._session = opts, session

    async def _run(self) -> None:
        request_id = utils.shortuuid()
        bstream = utils.audio.AudioByteStream(
            sample_rate=self._opts.sample_rate, num_channels=NUM_CHANNELS
        )

        json = _to_cartesia_options(self._opts)
        json["transcript"] = self._input_text

        headers = {
            API_AUTH_HEADER: self._opts.api_key,
            API_VERSION_HEADER: API_VERSION,
        }

        try:
            async with self._session.post(
                self._opts.get_http_url("/tts/bytes"),
                headers=headers,
                json=json,
                timeout=aiohttp.ClientTimeout(
                    total=30,
                    sock_connect=self._conn_options.timeout,
                ),
            ) as resp:
                resp.raise_for_status()
                emitter = tts.SynthesizedAudioEmitter(
                    event_ch=self._event_ch,
                    request_id=request_id,
                )
                async for data, _ in resp.content.iter_chunks():
                    for frame in bstream.write(data):
                        emitter.push(frame)

                for frame in bstream.flush():
                    emitter.push(frame)
                emitter.flush()
        except asyncio.TimeoutError as e:
            raise APITimeoutError() from e
        except aiohttp.ClientResponseError as e:
            raise APIStatusError(
                message=e.message,
                status_code=e.status,
                request_id=None,
                body=None,
            ) from e
        except Exception as e:
            raise APIConnectionError() from e
```

----------------------------------------

TITLE: Participant Property: name
DESCRIPTION: The participant's name. This property is intended for user-facing purposes, such as displaying the participant's name in a user interface.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room.participant/-remote-participant/index

LANGUAGE: APIDOC
CODE:
```
@FlowObservable
@get:FlowObservable
@set:VisibleForTesting
var name: String?
```

----------------------------------------

TITLE: Handle LiveKit Room and Track Events
DESCRIPTION: This comprehensive Python method, `_on_room_event`, processes a wide array of LiveKit room events. It manages participant states (connected, disconnected) and track lifecycles (published, unpublished, subscribed, unsubscribed, muted, subscription failed) for both local and remote participants, updating internal data structures and emitting corresponding events.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/rtc/room

LANGUAGE: python
CODE:
```
        def _on_room_event(self, event: proto_room.RoomEvent):
            which = event.WhichOneof("message")
            if which == "participant_connected":
                rparticipant = self._create_remote_participant(event.participant_connected.info)
                self.emit("participant_connected", rparticipant)
            elif which == "participant_disconnected":
                identity = event.participant_disconnected.participant_identity
                rparticipant = self._remote_participants.pop(identity)
                rparticipant._info.disconnect_reason = event.participant_disconnected.disconnect_reason
                self.emit("participant_disconnected", rparticipant)
            elif which == "local_track_published":
                sid = event.local_track_published.track_sid
                lpublication = self.local_participant.track_publications[sid]
                ltrack = lpublication.track
                self.emit("local_track_published", lpublication, ltrack)
            elif which == "local_track_unpublished":
                sid = event.local_track_unpublished.publication_sid
                lpublication = self.local_participant.track_publications[sid]
                self.emit("local_track_unpublished", lpublication)
            elif which == "local_track_subscribed":
                sid = event.local_track_subscribed.track_sid
                lpublication = self.local_participant.track_publications[sid]
                lpublication._first_subscription.set_result(None)
                self.emit("local_track_subscribed", lpublication.track)
            elif which == "track_published":
                rparticipant = self._remote_participants[event.track_published.participant_identity]
                rpublication = RemoteTrackPublication(event.track_published.publication)
                rparticipant._track_publications[rpublication.sid] = rpublication
                self.emit("track_published", rpublication, rparticipant)
            elif which == "track_unpublished":
                rparticipant = self._remote_participants[event.track_unpublished.participant_identity]
                rpublication = rparticipant._track_publications.pop(
                    event.track_unpublished.publication_sid
                )
                self.emit("track_unpublished", rpublication, rparticipant)
            elif which == "track_subscribed":
                owned_track_info = event.track_subscribed.track
                track_info = owned_track_info.info
                rparticipant = self._remote_participants[event.track_subscribed.participant_identity]
                rpublication = rparticipant.track_publications[track_info.sid]
                rpublication._subscribed = True
                if track_info.kind == TrackKind.KIND_VIDEO:
                    remote_video_track = RemoteVideoTrack(owned_track_info)
                    rpublication._track = remote_video_track
                    self.emit("track_subscribed", remote_video_track, rpublication, rparticipant)
                elif track_info.kind == TrackKind.KIND_AUDIO:
                    remote_audio_track = RemoteAudioTrack(owned_track_info)
                    rpublication._track = remote_audio_track
                    self.emit("track_subscribed", remote_audio_track, rpublication, rparticipant)
            elif which == "track_unsubscribed":
                identity = event.track_unsubscribed.participant_identity
                rparticipant = self._remote_participants[identity]
                rpublication = rparticipant.track_publications[event.track_unsubscribed.track_sid]
                rtrack = rpublication.track
                rpublication._track = None
                rpublication._subscribed = False
                self.emit("track_unsubscribed", rtrack, rpublication, rparticipant)
            elif which == "track_subscription_failed":
                identity = event.track_subscription_failed.participant_identity
                rparticipant = self._remote_participants[identity]
                error = event.track_subscription_failed.error
                self.emit(
                    "track_subscription_failed",
                    rparticipant,
                    event.track_subscription_failed.track_sid,
                    error,
                )
            elif which == "track_muted":
                identity = event.track_muted.participant_identity
                # TODO: pass participant identity
                participant = self._retrieve_participant(identity)
                assert isinstance(participant, Participant)
                publication = participant.track_publications[event.track_muted.track_sid]
                publication._info.muted = True
```

----------------------------------------

TITLE: LiveKit Room Event: ParticipantDisconnected
DESCRIPTION: Fires when a RemoteParticipant leaves the room *after* the local participant has joined.

SOURCE: https://docs.livekit.io/reference/client-sdk-js/enums/RoomEvent

LANGUAGE: APIDOC
CODE:
```
ParticipantDisconnected: "participantDisconnected"
args: (participant: RemoteParticipant)
```

----------------------------------------

TITLE: Wait for Specific Participant in LiveKit Room in Python
DESCRIPTION: Asynchronously waits for a remote participant to join the room, matching by identity or kind. If the participant is already present, it returns immediately. Raises a RuntimeError if the room is not connected.

SOURCE: https://docs.livekit.io/reference/python/livekit/agents/index

LANGUAGE: python
CODE:
```
async def wait_for_participant(
    self,
    *,
    identity: str | None = None,
    kind: list[rtc.ParticipantKind.ValueType]
    | rtc.ParticipantKind.ValueType = DEFAULT_PARTICIPANT_KINDS,
) -> rtc.RemoteParticipant:
    """
    Returns a participant that matches the given identity. If identity is None, the first
    participant that joins the room will be returned.
    If the participant has already joined, the function will return immediately.
    """
    if not self._room.isconnected():
        raise RuntimeError("room is not connected")

    fut = asyncio.Future[rtc.RemoteParticipant]()

    def kind_match(p: rtc.RemoteParticipant) -> bool:
        if isinstance(kind, list):
            return p.kind in kind

        return p.kind == kind

    for p in self._room.remote_participants.values():
        if (identity is None or p.identity == identity) and kind_match(p):
            fut.set_result(p)
            break

    def _on_participant_connected(p: rtc.RemoteParticipant):
        if (identity is None or p.identity == identity) and kind_match(p):
            self._room.off("participant_connected", _on_participant_connected)
            if not fut.done():
                fut.set_result(p)

    if not fut.done():
        self._room.on("participant_connected", _on_participant_connected)

    return await fut
```

----------------------------------------

TITLE: Perform an RPC Request to Another Participant
DESCRIPTION: This example demonstrates how a LiveKit participant can initiate an RPC call to another participant. It uses `room.localParticipant!.performRpc` to specify the `destinationIdentity`, `method` name, and `payload`. The call is wrapped in a `try-catch` block to handle potential errors, including `RpcError` types, and logs the response or error.

SOURCE: https://docs.livekit.io/reference/client-sdk-js

LANGUAGE: TypeScript
CODE:
```
try {
  const response = await room.localParticipant!.performRpc({
    destinationIdentity: 'recipient-identity',
    method: 'greet',
    payload: 'Hello from RPC!',
  });
  console.log('RPC response:', response);
} catch (error) {
  console.error('RPC call failed:', error);
}
```

----------------------------------------

TITLE: Initialize and Start LiveKit Voice Assistant
DESCRIPTION: This function initializes and starts the voice assistant within a LiveKit room. It sets up event listeners for various metrics (STT, TTS, LLM, VAD) and handles participant linking, either by a specified participant or by finding the first available in the room. It prevents multiple starts and manages the main asynchronous task.

SOURCE: https://docs.livekit.io/reference/python/livekit/agents/pipeline/pipeline_agent

LANGUAGE: python
CODE:
```
        def start(
            self, room: rtc.Room, participant: rtc.RemoteParticipant | str | None = None
        ) -> None:
            """Start the voice assistant

            Args:
                room: the room to use
                participant: the participant to listen to, can either be a participant or a participant identity
                    If None, the first participant found in the room will be selected
            """
            if self._started:
                raise RuntimeError("voice assistant already started")

            @self._stt.on("metrics_collected")
            def _on_stt_metrics(stt_metrics: metrics.STTMetrics) -> None:
                self.emit(
                    "metrics_collected",
                    metrics.PipelineSTTMetrics(
                        **stt_metrics.__dict__,
                    ),
                )

            @self._tts.on("metrics_collected")
            def _on_tts_metrics(tts_metrics: metrics.TTSMetrics) -> None:
                speech_data = SpeechDataContextVar.get(None)
                if speech_data is None:
                    return

                self.emit(
                    "metrics_collected",
                    metrics.PipelineTTSMetrics(
                        **tts_metrics.__dict__,
                        sequence_id=speech_data.sequence_id,
                    ),
                )

            @self._llm.on("metrics_collected")
            def _on_llm_metrics(llm_metrics: metrics.LLMMetrics) -> None:
                speech_data = SpeechDataContextVar.get(None)
                if speech_data is None:
                    return
                self.emit(
                    "metrics_collected",
                    metrics.PipelineLLMMetrics(
                        **llm_metrics.__dict__,
                        sequence_id=speech_data.sequence_id,
                    ),
                )

            @self._vad.on("metrics_collected")
            def _on_vad_metrics(vad_metrics: vad.VADMetrics) -> None:
                self.emit(
                    "metrics_collected", metrics.PipelineVADMetrics(**vad_metrics.__dict__)
                )

            room.on("participant_connected", self._on_participant_connected)
            self._room, self._participant = room, participant

            if participant is not None:
                if isinstance(participant, rtc.RemoteParticipant):
                    self._link_participant(participant.identity)
                else:
                    self._link_participant(participant)
            else:
                # no participant provided, try to find the first participant in the room
                for participant in self._room.remote_participants.values():
                    self._link_participant(participant.identity)
                    break

            self._main_atask = asyncio.create_task(self._main_task())
```

LANGUAGE: APIDOC
CODE:
```
Method: start(self, room: rtc.Room, participant: rtc.RemoteParticipant | str | None = None) -> None
  Description: Start the voice assistant
  Parameters:
    room: The room to use.
    participant: The participant to listen to, can either be a participant object or a participant identity string. If None, the first participant found in the room will be selected.
```

----------------------------------------

TITLE: Dart: Implementation of setAudioOutputDevice
DESCRIPTION: Provides the Dart implementation for the `setAudioOutputDevice` method. This code handles platform-specific logic (web vs. other platforms) for setting the audio output, iterates through participants' audio tracks on the web, and updates the room's default audio output options.

SOURCE: https://docs.livekit.io/reference/client-sdk-flutter/livekit_client/RoomHardwareManagementMethods/setAudioOutputDevice

LANGUAGE: Dart
CODE:
```
Future<void> setAudioOutputDevice(MediaDevice device) async {
  if (lkPlatformIs(PlatformType.web)) {
    participants.forEach((_, participant) {
      for (var audioTrack in participant.audioTracks) {
        audioTrack.track?.setSinkId(device.deviceId);
      }
    });
    Hardware.instance.selectedAudioOutput = device;
  } else {
    await Hardware.instance.selectAudioOutput(device);
  }
  engine.roomOptions = engine.roomOptions.copyWith(
    defaultAudioOutputOptions: roomOptions.defaultAudioOutputOptions.copyWith(
      deviceId: device.deviceId,
    ),
  );
}
```

----------------------------------------

TITLE: LiveKit Server API: Updating Participant Attributes/Metadata
DESCRIPTION: This snippet shows how to update attributes or metadata for any participant from the server side using the `RoomServiceClient` from `livekit-server-sdk`. It demonstrates calling `roomServiceClient.updateParticipant()` with the room name, participant identity, and the new attributes or metadata.

SOURCE: https://docs.livekit.io/home/client/state/participant-attributes

LANGUAGE: Node.js
CODE:
```
import { RoomServiceClient } from 'livekit-server-sdk';
const roomServiceClient = new RoomServiceClient('myhost', 'api-key', 'my secret');
roomServiceClient.updateParticipant('room', 'identity', {
attributes: {
myKey: 'myValue',
},
metadata: 'updated metadata',
});
```

----------------------------------------

TITLE: Python: Subscribe to Participant Connected Event
DESCRIPTION: Demonstrates how to subscribe to the `participant_connected` event on a LiveKit Room instance using a Python callback function. The callback is executed when a new participant joins the room, printing their identity.

SOURCE: https://docs.livekit.io/reference/python/livekit/rtc/index

LANGUAGE: python
CODE:
```
def on_participant_connected(participant):
    print(f"Participant connected: {participant.identity}")

room.on("participant_connected", on_participant_connected)
```

----------------------------------------

TITLE: LiveKit RoomService API Interface
DESCRIPTION: Defines the public interface for the LiveKit `RoomService` client, detailing its constructor and available methods for room management.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: APIDOC
CODE:
```
class RoomService (session: aiohttp.client.ClientSession, url: str, api_key: str, api_secret: str)
  Description: Client for LiveKit RoomService API
  Methods:
    __init__(session: aiohttp.ClientSession, url: str, api_key: str, api_secret: str)
      Description: Initializes the RoomService client.
    create_room(create: CreateRoomRequest) -> Room
      Description: Creates a new room with specified configuration.
      Parameters:
        create (CreateRoomRequest):
          - name: str - Unique room name
          - empty_timeout: int - Seconds to keep room open if empty
          - max_participants: int - Max allowed participants
          - metadata: str - Custom room metadata
          - egress: RoomEgress - Egress configuration
          - min_playout_delay: int - Minimum playout delay in ms
          - max_playout_delay: int - Maximum playout delay in ms
          - sync_streams: bool - Enable A/V sync for playout delays >200ms
      Returns:
        Room: The created room object
```

----------------------------------------

TITLE: Initiate RPC Call to Remote Participant (Kotlin)
DESCRIPTION: Initiates a Remote Procedure Call (RPC) to a specified remote participant. This function allows for inter-participant communication by sending a method name and payload, expecting a string response within a given timeout.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room.participant/-local-participant/index

LANGUAGE: APIDOC
CODE:
```
open suspend override fun performRpc(destinationIdentity: Participant.Identity, method: String, payload: String, responseTimeout: Duration): String
```

----------------------------------------

TITLE: LiveKit Room Service API: Send Data
DESCRIPTION: Documents the `send_data` method for sending data payloads to participants in a room, specifying delivery kind and optional targeting, along with its Python implementation.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: APIDOC
CODE:
```
send_data(send: SendDataRequest) -> SendDataResponse
  Description: Sends data to participants in a room.
  Parameters:
    send (SendDataRequest):
      - room: str - Room name
      - data: bytes - Data payload to send
      - kind: DataPacket.Kind - RELIABLE or LOSSY delivery
      - destination_identities: list[str] - Target participant identities
      - topic: str - Optional topic for the message
  Returns:
    SendDataResponse: Empty response object
```

LANGUAGE: python
CODE:
```
send.nonce = uuid4().bytes
return await self._client.request(
    SVC,
    "SendData",
    send,
    self._auth_header(VideoGrants(room_admin=True, room=send.room)),
    SendDataResponse,
)
```

----------------------------------------

TITLE: LiveKit Room Connection Internal Implementation (Python)
DESCRIPTION: This extensive Python code provides the full implementation details for connecting to a LiveKit room. It covers the construction of FFI requests, handling various `RoomOptions` (including E2EE and RTC configurations), managing FFI client interactions, processing responses, and initializing room state and participants.

SOURCE: https://docs.livekit.io/reference/python/livekit/rtc/index

LANGUAGE: python
CODE:
```
async def connect(self, url: str, token: str, options: RoomOptions = RoomOptions()) -> None:
    """Connects to a LiveKit room using the specified URL and token.

    Parameters:
        url (str): The WebSocket URL of the LiveKit server to connect to.
        token (str): The access token for authentication and authorization.
        options (RoomOptions, optional): Additional options for the room connection.

    Raises:
        ConnectError: If the connection fails.
    """
    req = proto_ffi.FfiRequest()
    req.connect.url = url
    req.connect.token = token

    # options
    req.connect.options.auto_subscribe = options.auto_subscribe
    req.connect.options.dynacast = options.dynacast

    if options.e2ee:
        req.connect.options.e2ee.encryption_type = options.e2ee.encryption_type
        req.connect.options.e2ee.key_provider_options.shared_key = (
            options.e2ee.key_provider_options.shared_key  # type: ignore
        )
        req.connect.options.e2ee.key_provider_options.ratchet_salt = (
            options.e2ee.key_provider_options.ratchet_salt
        )
        req.connect.options.e2ee.key_provider_options.failure_tolerance = (
            options.e2ee.key_provider_options.failure_tolerance
        )
        req.connect.options.e2ee.key_provider_options.ratchet_window_size = (
            options.e2ee.key_provider_options.ratchet_window_size
        )

    if options.rtc_config:
        req.connect.options.rtc_config.ice_transport_type = (
            options.rtc_config.ice_transport_type
        )  # type: ignore
        req.connect.options.rtc_config.continual_gathering_policy = (
            options.rtc_config.continual_gathering_policy
        )  # type: ignore
        req.connect.options.rtc_config.ice_servers.extend(options.rtc_config.ice_servers)

    # subscribe before connecting so we don't miss any events
    self._ffi_queue = FfiClient.instance.queue.subscribe(self._loop)

    queue = FfiClient.instance.queue.subscribe()
    try:
        resp = FfiClient.instance.request(req)
        cb: proto_ffi.FfiEvent = await queue.wait_for(
            lambda e: e.connect.async_id == resp.connect.async_id
        )
    finally:
        FfiClient.instance.queue.unsubscribe(queue)

    if cb.connect.error:
        FfiClient.instance.queue.unsubscribe(self._ffi_queue)
        raise ConnectError(cb.connect.error)

    self._ffi_handle = FfiHandle(cb.connect.result.room.handle.id)

    self._e2ee_manager = E2EEManager(self._ffi_handle.handle, options.e2ee)

    self._info = cb.connect.result.room.info
    self._connection_state = ConnectionState.CONN_CONNECTED

    self._local_participant = LocalParticipant(
        self._room_queue, cb.connect.result.local_participant

```

----------------------------------------

TITLE: LiveKit SDK: Handling Participant Attribute and Metadata Changes
DESCRIPTION: This code snippet demonstrates how LiveKit SDKs handle changes to participant attributes and metadata. It shows event listeners for `RoomEvent.ParticipantAttributesChanged` and `RoomEvent.ParticipantMetadataChanged` events, as well as methods to update the local participant's attributes and metadata. Participants require `canUpdateOwnMetadata` permission to update their own data.

SOURCE: https://docs.livekit.io/home/client/data/participant-attributes

LANGUAGE: javascript
CODE:
```
// receiving changes
room.on(
RoomEvent.ParticipantAttributesChanged,
(changed: Record<string, string>, participant: Participant) => {
console.log(
'participant attributes changed',
changed,
'all attributes',
participant.attributes,
);
},
);
room.on(
RoomEvent.ParticipantMetadataChanged,
(oldMetadata: string | undefined, participant: Participant) => {
console.log('metadata changed from', oldMetadata, participant.metadata);
},
);
// updating local participant
room.localParticipant.setAttributes({
myKey: 'myValue',
myOtherKey: 'otherValue',
});
room.localParticipant.setMetadata(
JSON.stringify({
some: 'values',
}),
);
```

----------------------------------------

TITLE: Participant Property: state
DESCRIPTION: The current state of the participant. This property reflects the participant's connection status and activity within the room.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room.participant/-remote-participant/index

LANGUAGE: APIDOC
CODE:
```
@FlowObservable
@get:FlowObservable
@set:VisibleForTesting
var state: Participant.State
```

----------------------------------------

TITLE: Update LiveKit Room Metadata
DESCRIPTION: This function updates the metadata associated with a LiveKit room. It requires administrator privileges for the room and returns the updated Room object.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: python
CODE:
```
async def update_room_metadata(self, update: UpdateRoomMetadataRequest) -> Room:
    """Updates a room's [metadata](https://docs.livekit.io/home/client/data/room-metadata/).

    Args:
        update (UpdateRoomMetadataRequest): arg containing:
            - room: str - Name of room to update
            - metadata: str - New metadata to set

    Returns:
        Room: Updated Room object
    """
    return await self._client.request(
        SVC,
        "UpdateRoomMetadata",
        update,
        self._auth_header(VideoGrants(room_admin=True, room=update.room)),
        Room,
    )
```

LANGUAGE: APIDOC
CODE:
```
Method: update_room_metadata
Signature: async def update_room_metadata(self, update: room.UpdateRoomMetadataRequest) -> models.Room
Description: Updates a room's metadata.
Args:
  update (UpdateRoomMetadataRequest):
    - room: str - Name of room to update
    - metadata: str - New metadata to set
Returns:
  Room: Updated Room object
```

----------------------------------------

TITLE: Registering Participant Connected Event Listener in Python
DESCRIPTION: This Python snippet demonstrates how to register a callback function for the 'participant_connected' event using the `room.on()` method. The callback function `on_participant_connected` is defined to print the identity of the newly connected participant.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/rtc/room

LANGUAGE: python
CODE:
```
def on_participant_connected(participant):
    print(f"Participant connected: {participant.identity}")

room.on("participant_connected", on_participant_connected)
```

----------------------------------------

TITLE: LiveKit React Hooks API Reference
DESCRIPTION: This section lists all available React hooks in the LiveKit SDK, each designed for specific real-time communication functionalities such as audio/video control, participant management, and room state handling.

SOURCE: https://docs.livekit.io/reference/components/react/hook/useconnectionstate

LANGUAGE: APIDOC
CODE:
```
LiveKit React Hooks:
- useAudioPlayback
- useAudioWaveform
- useChat
- useChatToggle
- useClearPinButton
- useConnectionQualityIndicator
- useConnectionState
- useCreateLayoutContext
- useDataChannel
- useDisconnectButton
- useEnsureCreateLayoutContext
- useEnsureLayoutContext
- useEnsureParticipant
- useEnsureRoom
- useEnsureTrackRef
- useFacingMode
- useFocusToggle
- useGridLayout
- useIsEncrypted
- useIsMuted
- useIsRecording
- useIsSpeaking
- useKrispNoiseFilter
- useLayoutContext
- useLiveKitRoom
- useLocalParticipant
- useLocalParticipantPermissions
- useMaybeLayoutContext
- useMaybeParticipantContext
- useMaybeRoomContext
- useMaybeTrackRefContext
- useMediaDevices
- useMediaDeviceSelect
- useMultibandTrackVolume
- usePagination
- useParticipantAttribute
- useParticipantAttributes
- useParticipantContext
- useParticipantInfo
- useParticipantPermissions
- useParticipants
- useParticipantTile
- useParticipantTracks
- usePersistentUserChoices
- usePinnedTracks
- usePreviewDevice
- usePreviewTracks
- useRemoteParticipant
- useRemoteParticipants
- useRoomContext
- useRoomInfo
- useSortedParticipants
- useSpeakingParticipants
- useStartAudio
- useStartVideo
- useSwipe
- useTextStream
- useToken
- useTrackByName
- useTrackMutedIndicator
- useTrackRefContext
- useTracks
- useTrackToggle
- useTrackTranscription
- useTrackVolume
- useTranscriptions
- useVisualStableUpdate
- useVoiceAssistant
```

----------------------------------------

TITLE: Implement LiveKit Agent Wait for Participant
DESCRIPTION: Asynchronously waits for a remote participant to join the LiveKit room, or immediately returns if the participant is already connected. It supports filtering by participant identity and kind, and raises an error if the room is not connected.

SOURCE: https://docs.livekit.io/reference/python/livekit/agents/index

LANGUAGE: python
CODE:
```
async def wait_for_participant(
    self,
    *,
    identity: str | None = None,
    kind: list[rtc.ParticipantKind.ValueType]
    | rtc.ParticipantKind.ValueType = DEFAULT_PARTICIPANT_KINDS,
) -> rtc.RemoteParticipant:
    """
    Returns a participant that matches the given identity. If identity is None, the first
    participant that joins the room will be returned.
    If the participant has already joined, the function will return immediately.
    """
    if not self._room.isconnected():
        raise RuntimeError("room is not connected")

    fut = asyncio.Future[rtc.RemoteParticipant]()

    def kind_match(p: rtc.RemoteParticipant) -> bool:
        if isinstance(kind, list):
            return p.kind in kind

        return p.kind == kind

    for p in self._room.remote_participants.values():
        if (identity is None or p.identity == identity) and kind_match(p):
            fut.set_result(p)
            break

    def _on_participant_connected(p: rtc.RemoteParticipant):
        if (identity is None or p.identity == identity) and kind_match(p):
            self._room.off("participant_connected", _on_participant_connected)
            if not fut.done():
                fut.set_result(p)

    if not fut.done():
```

----------------------------------------

TITLE: RemoteParticipant Class Definition and Constructor
DESCRIPTION: Defines the `RemoteParticipant` class, a representation of a remote participant in a LiveKit room, inheriting from `Participant`. It details the constructor's parameters, including `sid`, `identity`, `signalClient`, `ioDispatcher`, and `defaultDispatcher`.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room.participant/-remote-participant/index

LANGUAGE: APIDOC
CODE:
```
class RemoteParticipant : Participant

  __init__(
    sid: Participant.Sid,
    identity: Participant.Identity? = null,
    signalClient: SignalClient,
    ioDispatcher: CoroutineDispatcher,
    defaultDispatcher: CoroutineDispatcher
  )
    sid: The unique identifier for the participant.
    identity: An optional identity string for the participant.
    signalClient: The client used for signaling.
    ioDispatcher: The CoroutineDispatcher for I/O operations.
    defaultDispatcher: The default CoroutineDispatcher for general operations.
```

----------------------------------------

TITLE: LiveKit Android SDK: RoomEvent.ParticipantDisconnected.participant Property
DESCRIPTION: Details the `participant` property of the `RoomEvent.ParticipantDisconnected` event, which provides access to the `RemoteParticipant` object that has disconnected from the room.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.events/-room-event/-participant-disconnected/participant

LANGUAGE: APIDOC
CODE:
```
RoomEvent.ParticipantDisconnected:
  Properties:
    participant: RemoteParticipant
      Description: The remote participant associated with this event.
```

----------------------------------------

TITLE: e2eeManager Property
DESCRIPTION: Provides access to the End-to-End Encryption (E2EE) manager. This manager handles the encryption and decryption of media streams within the room, if E2EE is enabled.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room/-room/index

LANGUAGE: APIDOC
CODE:
```
var e2eeManager: E2EEManager?
```

----------------------------------------

TITLE: Participant Constructor Implementation (Dart)
DESCRIPTION: Dart implementation of the `Participant` constructor, showing how it initializes properties like room, sid, identity, and name. It also sets up event listeners to trigger `ChangeNotifier` updates and includes logic for resource disposal upon `onDispose`.

SOURCE: https://docs.livekit.io/reference/client-sdk-flutter/livekit_client/Participant/Participant

LANGUAGE: Dart
CODE:
```
@internal
Participant({
  required this.room,
  required this.sid,
  required this.identity,
  required String name,
}) : _name = name {
  // Any event emitted will trigger ChangeNotifier
  events.listen((event) {
    logger.fine('[ParticipantEvent] $event, will notifyListeners()');
    notifyListeners();
  });

  onDispose(() async {
    await events.dispose();
    await unpublishAllTracks();
  });
}
```

----------------------------------------

TITLE: Establish LiveKit Room Scope in Compose
DESCRIPTION: Establishes a Composable scope that manages a LiveKit Room object. This function handles connection, disconnection, and error handling, making the Room object accessible via RoomLocal within its content block.

SOURCE: https://docs.livekit.io/reference/components-android/livekit-compose-components/io.livekit.android.compose.local/index

LANGUAGE: APIDOC
CODE:
```
@Composable
fun RoomScope(url: String? = null, token: String? = null, audio: Boolean = false, video: Boolean = false, connect: Boolean = true, roomOptions: RoomOptions? = null, liveKitOverrides: LiveKitOverrides? = null, connectOptions: ConnectOptions? = null, onConnected: suspend CoroutineScope.(Room) -> Unit? = null, onDisconnected: suspend CoroutineScope.(Room) -> Unit? = null, onError: (Room, Exception?) -> Unit? = null, passedRoom: Room? = null, content: @Composable (room: Room) -> Unit)
  url: String? = null - The URL of the LiveKit server.
  token: String? = null - The authentication token for the room.
  audio: Boolean = false - Whether to enable audio when connecting.
  video: Boolean = false - Whether to enable video when connecting.
  connect: Boolean = true - Whether to automatically connect to the room.
  roomOptions: RoomOptions? = null - Optional configuration for the room.
  liveKitOverrides: LiveKitOverrides? = null - Optional overrides for LiveKit client behavior.
  connectOptions: ConnectOptions? = null - Optional configuration for the connection process.
  onConnected: suspend CoroutineScope.(Room) -> Unit? = null - Callback invoked upon successful connection to the room.
  onDisconnected: suspend CoroutineScope.(Room) -> Unit? = null - Callback invoked when disconnected from the room.
  onError: (Room, Exception?) -> Unit? = null - Callback invoked when an error occurs in the room.
  passedRoom: Room? = null - An optional pre-existing Room object to use instead of creating a new one.
  content: @Composable (room: Room) -> Unit - The Composable content to be rendered within the room's scope, receiving the Room object.
Establishes a room scope which remembers a Room object which can be accessed through the RoomLocal composition local.
```

----------------------------------------

TITLE: Define and Implement STTSegmentsForwarder Class in Python
DESCRIPTION: This class is responsible for forwarding Speech-to-Text (STT) transcriptions to users, primarily for client-side rendering. It initializes with room, participant, and track details, managing a queue for transcription segments and handling their publication to the LiveKit room. It also includes a callback for pre-processing transcriptions.

SOURCE: https://docs.livekit.io/reference/python/livekit/agents/transcription/index

LANGUAGE: APIDOC
CODE:
```
STTSegmentsForwarder:
  __init__(*, room: rtc.Room, participant: rtc.Participant | str, track: rtc.Track | rtc.TrackPublication | str | None = None, before_forward_cb: BeforeForwardCallback = <function _default_before_forward_cb>, will_forward_transcription: WillForwardTranscription | None = None)
    Description: Initializes the STTSegmentsForwarder to manage and forward STT transcriptions.
    Parameters:
      room: rtc.Room - The LiveKit room instance where transcriptions will be published.
      participant: rtc.Participant | str - The participant identity or object associated with the transcription.
      track: rtc.Track | rtc.TrackPublication | str | None - Optional. The track SID or object to associate with the transcription. If None, attempts to find a micro track.
      before_forward_cb: BeforeForwardCallback - Optional. A callback function to process the transcription before it is forwarded. Defaults to _default_before_forward_cb.
      will_forward_transcription: WillForwardTranscription | None - Deprecated. Use `before_forward_cb` instead.
```

LANGUAGE: python
CODE:
```
class STTSegmentsForwarder:
    """
    Forward STT transcription to the users. (Useful for client-side rendering)
    """

    def __init__(
        self,
        *,
        room: rtc.Room,
        participant: rtc.Participant | str,
        track: rtc.Track | rtc.TrackPublication | str | None = None,
        before_forward_cb: BeforeForwardCallback = _default_before_forward_cb,
        # backward compatibility
        will_forward_transcription: WillForwardTranscription | None = None,
    ):
        identity = participant if isinstance(participant, str) else participant.identity
        if track is None:
            track = _utils.find_micro_track_id(room, identity)
        elif isinstance(track, (rtc.TrackPublication, rtc.Track)):
            track = track.sid

        if will_forward_transcription is not None:
            logger.warning(
                "will_forward_transcription is deprecated and will be removed in 1.5.0, use before_forward_cb instead",
            )
            before_forward_cb = will_forward_transcription

        self._room, self._participant_identity, self._track_id = room, identity, track
        self._before_forward_cb = before_forward_cb
        self._queue = asyncio.Queue[Optional[rtc.TranscriptionSegment]]()
        self._main_task = asyncio.create_task(self._run())
        self._current_id = _utils.segment_uuid()

    async def _run(self):
        try:
            while True:
                seg = await self._queue.get()
                if seg is None:
                    break

                base_transcription = rtc.Transcription(
                    participant_identity=self._participant_identity,
                    track_sid=self._track_id,
                    segments=[seg],  # no history for now
                )

                transcription = self._before_forward_cb(self, base_transcription)
                if asyncio.iscoroutine(transcription):
                    transcription = await transcription

                if not isinstance(transcription, rtc.Transcription):
                    transcription = _default_before_forward_cb(self, base_transcription)

                if transcription.segments and self._room.isconnected():
                    await self._room.local_participant.publish_transcription(
                        transcription
                    )

        except Exception:
            logger.exception("error in stt transcription")

    def update(self, ev: stt.SpeechEvent):
        if ev.type == stt.SpeechEventType.INTERIM_TRANSCRIPT:
            # TODO(theomonnom): We always take the first alternative, we should mb expose opt to the
            # user?
            text = ev.alternatives[0].text
            self._queue.put_nowait(
                rtc.TranscriptionSegment(
                    id=self._current_id,
                    text=text,
                    start_time=0,
                    end_time=0,
                    final=False,
                    language="",  # TODO
                )
            )
        elif ev.type == stt.SpeechEventType.FINAL_TRANSCRIPT:
            text = ev.alternatives[0].text
            self._queue.put_nowait(
                rtc.TranscriptionSegment(
                    id=self._current_id,
                    text=text,
                    start_time=0,
                    end_time=0,
                    final=True,
                    language="",  # TODO
                )
            )

            self._current_id = _utils.segment_uuid()

    async def aclose(self, *, wait: bool = True) -> None:
        self._queue.put_nowait(None)

        if not wait:
            self._main_task.cancel()

        with contextlib.suppress(asyncio.CancelledError):
            await self._main_task
```

----------------------------------------

TITLE: LiveKit Room Service: delete_room
DESCRIPTION: API documentation for deleting a LiveKit room. Details the request parameter for identifying the room to delete and the empty response.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: APIDOC
CODE:
```
async def delete_room(self, delete: room.DeleteRoomRequest) -> room.DeleteRoomResponse
  delete: DeleteRoomRequest
    - room: str - Name of room to delete
  Returns: DeleteRoomResponse - Empty response object
```

----------------------------------------

TITLE: Delete a LiveKit Room
DESCRIPTION: This snippet illustrates how to delete a specific room by its name using the RoomServiceClient in Go. Deleting a room will immediately cause all connected participants to be disconnected.

SOURCE: https://docs.livekit.io/home/server/managing-rooms

LANGUAGE: Go
CODE:
```
_, _ = roomClient.DeleteRoom(context.Background(), &livekit.DeleteRoomRequest{
	Room: "myroom",
})
```

----------------------------------------

TITLE: Dart Implementation: Room participants Property Getter
DESCRIPTION: Provides the Dart implementation for the `participants` getter in the `Room` class. It returns an `UnmodifiableMapView` of the internal `_participants` map, ensuring that the collection cannot be modified externally.

SOURCE: https://docs.livekit.io/reference/client-sdk-flutter/livekit_client/Room/participants

LANGUAGE: Dart
CODE:
```
UnmodifiableMapView<String, RemoteParticipant> get participants =>
    UnmodifiableMapView(_participants);
```

----------------------------------------

TITLE: API Reference: livekit.agents.RoomIO
DESCRIPTION: Details the `RoomIO` class from `livekit.agents`, which handles input and output operations within a LiveKit room. It provides methods for managing audio, video, and transcription streams, as well as participant interactions.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/agents/index

LANGUAGE: APIDOC
CODE:
```
RoomIO:
  aclose()
  audio_input()
  audio_output()
  linked_participant()
  set_participant()
  start()
  subscribed_fut()
  transcription_output()
  unset_participant()
  video_input()
```

----------------------------------------

TITLE: Monitor LiveKit Active Speakers and Speaking Status (JavaScript)
DESCRIPTION: Demonstrates how to listen for active speaker changes (`RoomEvent.ActiveSpeakersChanged`) and individual participant speaking status changes (`ParticipantEvent.IsSpeakingChanged`) in LiveKit. These events fire on `Room` and `Participant` objects, enabling UI updates based on who is currently speaking.

SOURCE: https://docs.livekit.io/guides/room/receive

LANGUAGE: JavaScript
CODE:
```
room.on(RoomEvent.ActiveSpeakersChanged, (speakers: Participant[]) => {
// Speakers contain all of the current active speakers
});

participant.on(ParticipantEvent.IsSpeakingChanged, (speaking: boolean) => {
console.log(
`${participant.identity} is ${speaking ? 'now' : 'no longer'} speaking. audio level: ${participant.audioLevel}`,
);
});
```

----------------------------------------

TITLE: Add Participant Entrypoint Function in LiveKit Room in Python
DESCRIPTION: Registers a function to be executed when a participant joins the room, or immediately if the participant is already present. Multiple unique entrypoints can be added and will run in parallel for each participant. Raises a ValueError if an entrypoint is added more than once.

SOURCE: https://docs.livekit.io/reference/python/livekit/agents/index

LANGUAGE: python
CODE:
```
def add_participant_entrypoint(
    self,
    entrypoint_fnc: Callable[
        [JobContext, rtc.RemoteParticipant], Coroutine[None, None, None]
    ],
    *_,
    kind: list[rtc.ParticipantKind.ValueType]
    | rtc.ParticipantKind.ValueType = DEFAULT_PARTICIPANT_KINDS,
):
    """Adds an entrypoint function to be run when a participant joins the room. In cases where
    the participant has already joined, the entrypoint will be run immediately. Multiple unique entrypoints can be
    added and they will each be run in parallel for each participant.
    """

    if entrypoint_fnc in [e for (e, _) in self._participant_entrypoints]:
        raise ValueError("entrypoints cannot be added more than once")

    self._participant_entrypoints.append((entrypoint_fnc, kind))
```

----------------------------------------

TITLE: Participant Property: sid
DESCRIPTION: The unique identifier for this participant. This SID (Session ID) is a stable and distinct string used to reference the participant.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room.participant/-remote-participant/index

LANGUAGE: APIDOC
CODE:
```
var sid: Participant.Sid
```

----------------------------------------

TITLE: LiveKit Room Service: create_room
DESCRIPTION: API documentation for creating a new LiveKit room. Specifies input parameters for room configuration and the expected return type.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: APIDOC
CODE:
```
async def create_room(self, create: room.CreateRoomRequest) -> models.Room
  create: CreateRoomRequest
    - name: str - Unique room name
    - empty_timeout: int - Seconds to keep room open if empty
    - max_participants: int - Max allowed participants
    - metadata: str - Custom room metadata
    - egress: RoomEgress - Egress configuration
    - min_playout_delay: int - Minimum playout delay in ms
    - max_playout_delay: int - Maximum playout delay in ms
    - sync_streams: bool - Enable A/V sync for playout delays >200ms
  Returns: Room - The created room object
```

----------------------------------------

TITLE: LiveKit Android SDK: RoomEvent.ParticipantConnected Constructor
DESCRIPTION: Documents the constructor for the `ParticipantConnected` event, which is triggered when a remote participant connects to a room. It requires instances of `Room` and `RemoteParticipant` as parameters.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.events/-room-event/-participant-connected/-participant-connected

LANGUAGE: APIDOC
CODE:
```
Class: io.livekit.android.events.RoomEvent.ParticipantConnected
  Constructor:
    signature: constructor(room: io.livekit.android.room.Room, participant: io.livekit.android.room.participant.RemoteParticipant)
    parameters:
      room: io.livekit.android.room.Room
        Description: The Room instance associated with the event.
      participant: io.livekit.android.room.participant.RemoteParticipant
        Description: The remote participant who connected.
```

----------------------------------------

TITLE: Room Class Initialization
DESCRIPTION: Initializes a new `Room` instance, serving as the central object for managing a LiveKit room. It sets up the event loop, internal queues, and dictionaries for managing remote participants, connection state, and data streams.

SOURCE: https://docs.livekit.io/reference/python/livekit/rtc/index

LANGUAGE: python
CODE:
```
class Room(EventEmitter[EventTypes]):
        def __init__(
            self,
            loop: Optional[asyncio.AbstractEventLoop] = None,
        ) -> None:
            """Initializes a new Room instance.

            Parameters:
                loop (Optional[asyncio.AbstractEventLoop]): The event loop to use. If not provided, the default event loop is used.
            """
            super().__init__()

            self._ffi_handle: Optional[FfiHandle] = None
            self._loop = loop or asyncio.get_event_loop()
            self._room_queue = BroadcastQueue[proto_ffi.FfiEvent]()
            self._info = proto_room.RoomInfo()
            self._rpc_invocation_tasks: set[asyncio.Task] = set()
            self._data_stream_tasks: set[asyncio.Task] = set()

            self._remote_participants: Dict[str, RemoteParticipant] = {}
            self._connection_state = ConnectionState.CONN_DISCONNECTED
            self._first_sid_future = asyncio.Future[str]()
            self._local_participant: LocalParticipant | None = None

            self._text_stream_readers: Dict[str, TextStreamReader] = {}
```

----------------------------------------

TITLE: LiveKit Room Service API: Mute/Unmute Published Track
DESCRIPTION: Documents the `mute_published_track` method for controlling the mute state of a participant's published track, including its Python usage.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: APIDOC
CODE:
```
mute_published_track(update: MuteRoomTrackRequest) -> MuteRoomTrackResponse
  Description: Mutes or unmutes a participant's published track.
  Parameters:
    update (MuteRoomTrackRequest):
      - room: str - Room name
      - identity: str - Participant identity
      - track_sid: str - Track session ID to mute
      - muted: bool - True to mute, False to unmute
  Returns:
    MuteRoomTrackResponse:
      - track: TrackInfo - Updated track information
```

LANGUAGE: python
CODE:
```
return await self._client.request(
    SVC,
    "MutePublishedTrack",
    update,
    self._auth_header(VideoGrants(room_admin=True, room=update.room)),
    MuteRoomTrackResponse,
)
```

----------------------------------------

TITLE: LiveKit Android SDK: Get Participant by Identity
DESCRIPTION: Retrieves a participant from the LiveKit room using their unique identity. This function provides two overloads: one accepting a String identity and another accepting a Participant.Identity object. It returns the corresponding Participant object if found, or null otherwise.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room/-room/get-participant-by-identity

LANGUAGE: APIDOC
CODE:
```
Function: getParticipantByIdentity
Description: Retrieves a participant from the room by their unique identity.

Overloads:
  1. fun getParticipantByIdentity(identity: String): Participant?
     Parameters:
       identity: String - The unique identity string of the participant.
     Returns:
       Participant? - The Participant object if found, otherwise null.

  2. fun getParticipantByIdentity(identity: Participant.Identity): Participant?
     Parameters:
       identity: Participant.Identity - The identity object of the participant.
     Returns:
       Participant? - The Participant object if found, otherwise null.
```

----------------------------------------

TITLE: Retrieve Participant by Identity
DESCRIPTION: Fetches a participant object from the room using their unique identity string or a Participant.Identity object. Returns null if no participant with the given identity is found.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room/-room/index

LANGUAGE: APIDOC
CODE:
```
fun getParticipantByIdentity(identity: Participant.Identity): Participant?
```

LANGUAGE: APIDOC
CODE:
```
fun getParticipantByIdentity(identity: String): Participant?
```

----------------------------------------

TITLE: List LiveKit Rooms
DESCRIPTION: Lists active rooms. This method allows filtering rooms by an optional list of names. It returns a response object containing a list of active Room objects.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: APIDOC
CODE:
```
list_rooms(list: ListRoomsRequest) -> ListRoomsResponse
  Lists active rooms.
  Args:
    list (ListRoomsRequest): arg containing:
      - names: list[str] - Optional list of room names to filter by
  Returns:
    ListRoomsResponse:
      - rooms: list[Room] - List of active Room objects
```

LANGUAGE: python
CODE:
```
async def list_rooms(self, list: ListRoomsRequest) -> ListRoomsResponse:
    return await self._client.request(
        SVC,
        "ListRooms",
        list,
        self._auth_header(VideoGrants(room_list=True)),
        ListRoomsResponse,
    )
```

----------------------------------------

TITLE: LiveKit Room Method: getParticipantByIdentity
DESCRIPTION: Retrieves a participant from the room by their identity string.

SOURCE: https://docs.livekit.io/client-sdk-js/classes/Room

LANGUAGE: APIDOC
CODE:
```
getParticipantByIdentity(identity: string): undefined | Participant
  identity: string
```

----------------------------------------

TITLE: Get Room Local Participant (Python)
DESCRIPTION: Retrieves the local participant object for the LiveKit room. This object represents the current user in the room.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/rtc/index

LANGUAGE: Python
CODE:
```
@property
def local_participant(self) -> LocalParticipant:
    """Gets the local participant in the room.

    Returns:
        LocalParticipant: The local participant in the room.
    """
    if self._local_participant is None:
        raise Exception("cannot access local participant before connecting")

    return self._local_participant
```

----------------------------------------

TITLE: Receive DTMF Tones as LiveKit Room Events
DESCRIPTION: This code shows how to listen for incoming DTMF tones that are relayed from SIP participants to the room. Participants can subscribe to the `RoomEvent.DtmfReceived` event to process received DTMF codes and digits, along with the participant who sent them.

SOURCE: https://docs.livekit.io/sip/dtmf

LANGUAGE: Node.js
CODE:
```
room.on(RoomEvent.DtmfReceived, (code, digit, participant) => {
console.log('DTMF received from participant', participant.identity, code, digit);
});
```

----------------------------------------

TITLE: LiveKit Android SDK: RoomEvent.ConnectionQualityChanged.participant Property
DESCRIPTION: Documents the 'participant' property of the `RoomEvent.ConnectionQualityChanged` event in the LiveKit Android SDK. This property identifies the participant whose connection quality has changed, which can be either a remote participant or the local participant (`Room.localParticipant`).

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.events/-room-event/-connection-quality-changed/participant

LANGUAGE: APIDOC
CODE:
```
Property: participant
  Type: Participant
  Description: Either a remote participant or Room.localParticipant
```

----------------------------------------

TITLE: Update LiveKit Room Metadata
DESCRIPTION: Updates the metadata for an existing room. This allows for dynamic modification of room properties. The method takes the room name and the new metadata string, returning the updated Room object.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/api/room_service

LANGUAGE: APIDOC
CODE:
```
update_room_metadata(update: UpdateRoomMetadataRequest) -> Room
  Updates a room's metadata.
  Args:
    update (UpdateRoomMetadataRequest): arg containing:
      - room: str - Name of room to update
      - metadata: str - New metadata to set
  Returns:
    Room: Updated Room object
```

LANGUAGE: python
CODE:
```
async def update_room_metadata(self, update: UpdateRoomMetadataRequest) -> Room:
    return await self._client.request(
        SVC,
        "UpdateRoomMetadata",
        update,
        self._auth_header(VideoGrants(room_admin=True, room=update.room)),
        Room,
    )
```

----------------------------------------

TITLE: Get Participant by Identity (Kotlin)
DESCRIPTION: Retrieves a participant from the room using their unique identity. Overloaded to accept either a Participant.Identity object or a String.

SOURCE: https://docs.livekit.io/client-sdk-android/livekit-android-sdk/io.livekit.android.room/-room/index

LANGUAGE: Kotlin
CODE:
```
fun getParticipantByIdentity(identity: Participant.Identity): Participant?
```

LANGUAGE: Kotlin
CODE:
```
fun getParticipantByIdentity(identity: String): Participant?
```

----------------------------------------

TITLE: Handle Track Published Event
DESCRIPTION: Callback function invoked when a new track is published to the room after the local participant has already joined. Provides details about the published track and the publishing participant.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room/-room/index

LANGUAGE: APIDOC
CODE:
```
open fun onTrackPublished(publication: RemoteTrackPublication, participant: RemoteParticipant)
```

----------------------------------------

TITLE: TrackSubscriptionPermissionChanged Event Participant Property
DESCRIPTION: Defines the `participant` property available within the `TrackSubscriptionPermissionChanged` event. This property provides a reference to the `RemoteParticipant` associated with the permission change, allowing access to the participant's details.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.events/-room-event/-track-subscription-permission-changed/participant

LANGUAGE: Kotlin
CODE:
```
val participant: RemoteParticipant
```

LANGUAGE: APIDOC
CODE:
```
Class: TrackSubscriptionPermissionChanged
  Property: participant
    Type: RemoteParticipant
    Description: The remote participant whose track subscription permissions have changed.
```

----------------------------------------

TITLE: Handle Received Data
DESCRIPTION: Callback function invoked when binary data is received from another participant in the room. The `data` parameter contains the received byte array, and `participant` identifies the sender.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room/-room/index

LANGUAGE: APIDOC
CODE:
```
open fun onDataReceived(data: ByteArray, participant: RemoteParticipant)
```

----------------------------------------

TITLE: Participant Class Constructor API Reference
DESCRIPTION: Documents the constructor for the `Participant` class, outlining its required and optional parameters, including the participant's session ID, identity, and the CoroutineDispatcher used for internal operations.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room.participant/-participant/-participant

LANGUAGE: APIDOC
CODE:
```
Participant:
  constructor(sid: Participant.Sid, identity: Participant.Identity? = null, @Named(value = "dispatcher_default") coroutineDispatcher: CoroutineDispatcher)
    Parameters:
      sid: Participant.Sid - The unique session identifier for the participant.
      identity: Participant.Identity? = null - An optional identity string for the participant.
      coroutineDispatcher: CoroutineDispatcher - The CoroutineDispatcher used for managing coroutine execution within the participant's operations.
```

----------------------------------------

TITLE: Publish Arbitrary Data to LiveKit Room (Python)
DESCRIPTION: This Python function allows publishing arbitrary byte or string data to a LiveKit room. It handles data encoding, constructs an FfiRequest for data publishing, and manages the asynchronous response. The function supports reliable transmission, targeting specific participants, and associating data with a topic.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/rtc/index

LANGUAGE: python
CODE:
```
async def publish_data(
    self,
    payload: Union[bytes, str],
    *,
    reliable: bool = True,
    destination_identities: List[str] = [],
    topic: str = "",
) -> None:
    """
    Publish arbitrary data to the room.

    Args:
        payload (Union[bytes, str]): The data to publish.
        reliable (bool, optional): Whether to send reliably or not. Defaults to True.
        destination_identities (List[str], optional): List of participant identities to send to. Defaults to [].
        topic (str, optional): The topic under which to publish the data. Defaults to "".

    Raises:
        PublishDataError: If there is an error in publishing data.
    """
    if isinstance(payload, str):
        payload = payload.encode("utf-8")

    data_len = len(payload)
    cdata = (ctypes.c_byte * data_len)(*payload)

    req = proto_ffi.FfiRequest()
    req.publish_data.local_participant_handle = self._ffi_handle.handle
    req.publish_data.data_ptr = ctypes.addressof(cdata)
    req.publish_data.data_len = data_len
    req.publish_data.reliable = reliable
    req.publish_data.topic = topic
    req.publish_data.destination_identities.extend(destination_identities)

    queue = FfiClient.instance.queue.subscribe()
    try:
        resp = FfiClient.instance.request(req)
        cb: proto_ffi.FfiEvent = await queue.wait_for(
            lambda e: e.publish_data.async_id == resp.publish_data.async_id
        )
finally:
    FfiClient.instance.queue.unsubscribe(queue)

    if cb.publish_data.error:
        raise PublishDataError(cb.publish_data.error)
```

LANGUAGE: APIDOC
CODE:
```
async def publish_data(self, payload: Union[bytes, str], *, reliable: bool = True, destination_identities: List[str] = [], topic: str = '') -> None
  Publish arbitrary data to the room.

  Args:
    payload (Union[bytes, str]): The data to publish.
    reliable (bool, optional): Whether to send reliably or not. Defaults to True.
    destination_identities (List[str], optional): List of participant identities to send to. Defaults to [].
    topic (str, optional): The topic under which to publish the data. Defaults to "".

  Raises:
    PublishDataError: If there is an error in publishing data.
```

----------------------------------------

TITLE: useToken Hook
DESCRIPTION: Manages and retrieves authentication tokens for connecting to LiveKit rooms. Essential for secure room access.

SOURCE: https://docs.livekit.io/reference/components/react/hook/usevisualstableupdate

LANGUAGE: APIDOC
CODE:
```
useToken
```

----------------------------------------

TITLE: LocalParticipant.registerRpcMethod API Reference
DESCRIPTION: Detailed API specification for the `registerRpcMethod` function of the `LocalParticipant` class in LiveKit Android SDK, including its signature, parameters (`method`, `handler`), and their descriptions. It also outlines the parameters passed to the `RpcHandler` and expected return types.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room.participant/-local-participant/register-rpc-method

LANGUAGE: APIDOC
CODE:
```
LocalParticipant.registerRpcMethod:
  Signature: open suspend override fun registerRpcMethod(method: String, handler: RpcHandler)
  Description: Establishes the participant as a receiver for calls of the specified RPC method. Will overwrite any existing callback for the same method.
  Parameters:
    method: String - The name of the indicated RPC method
    handler: RpcHandler - Will be invoked when an RPC request for this method is received
  Returns: Unit (implicitly)
  Throws:
    RpcError (with custom message)
    1500 ("Application Error") for other unhandled exceptions
  RpcHandler Parameters (RpcInvocationData):
    requestId: String - A unique identifier for this RPC request
    callerIdentity: String - The identity of the RemoteParticipant who initiated the RPC call
    payload: String - The data sent by the caller
    responseTimeout: Long - The maximum time available to return a response
  RpcHandler Return: String (expected response)
```

----------------------------------------

TITLE: UpdateRoomMetadata API Endpoint
DESCRIPTION: Update room metadata. A metadata update will be broadcast to all participants in the room. Requires `roomAdmin`

SOURCE: https://docs.livekit.io/reference/server/server-apis

LANGUAGE: APIDOC
CODE:
```
UpdateRoomMetadata
  room: string (Required) -
  metadata: string (Required) - user-provided payload; opaque to LiveKit
```

----------------------------------------

TITLE: LiveKit RtcConfiguration Class Reference
DESCRIPTION: Documentation for the `RtcConfiguration` class, which specifies WebRTC configuration parameters such as ICE servers, ICE transport type, and continual gathering policy for establishing peer connections in LiveKit.

SOURCE: https://docs.livekit.io/reference/python/livekit/rtc/room

LANGUAGE: APIDOC
CODE:
```
RtcConfiguration:
  - continual_gathering_policy
  - ice_servers
  - ice_transport_type
```

----------------------------------------

TITLE: Simulate Participants
DESCRIPTION: Allows populating a room with simulated participants for testing or demonstration purposes. No actual connection to a server is established; all state is managed locally. This is an experimental feature.

SOURCE: https://docs.livekit.io/reference/client-sdk-js/classes/Room

LANGUAGE: APIDOC
CODE:
```
simulateParticipants(options: SimulationOptions): Promise<void>
  Parameters:
    options: SimulationOptions
  Returns: Promise<void>
```

----------------------------------------

TITLE: Connect to LiveKit Room and Publish Local Media
DESCRIPTION: This JavaScript code snippet illustrates the basic steps to connect to a LiveKit room. It initializes a `Room` object, connects using a WebSocket URL and a generated token, logs the successful connection, and then enables and publishes the local participant's camera and microphone tracks. A note emphasizes that tokens should be generated server-side in production applications.

SOURCE: https://docs.livekit.io/home/quickstarts/javascript

LANGUAGE: javascript
CODE:
```
import { Room } from 'livekit-client';

const wsURL = '<your LiveKit server URL>';
const token = '<generate a token>';

const room = new Room();

await room.connect(wsURL, token);
console.log('connected to room', room.name);

// Publish local camera and mic tracks
await room.localParticipant.enableCameraAndMicrophone();
```

----------------------------------------

TITLE: Initialize LiveKit RoomServiceClient
DESCRIPTION: This snippet demonstrates how to initialize the LiveKit RoomServiceClient in Go. This client is essential for performing all room management operations and requires your LiveKit host URL, API key, and secret key for authentication.

SOURCE: https://docs.livekit.io/home/server/managing-rooms

LANGUAGE: Go
CODE:
```
import (
	lksdk "github.com/livekit/server-sdk-go"
	livekit "github.com/livekit/protocol/livekit"
)

// ...

host := "https://my.livekit.host"
roomClient := lksdk.NewRoomServiceClient(host, "api-key", "secret-key")
```

----------------------------------------

TITLE: RemoteParticipant Class Constructor Definition
DESCRIPTION: Documents the constructor for the `RemoteParticipant` class in the LiveKit Android SDK. It specifies the required parameters, their types, and default values where applicable, providing a clear signature for instantiation.

SOURCE: https://docs.livekit.io/reference/client-sdk-android/livekit-android-sdk/io.livekit.android.room.participant/-remote-participant/-remote-participant

LANGUAGE: APIDOC
CODE:
```
RemoteParticipant:
  constructor(sid: Participant.Sid, identity: Participant.Identity? = null, signalClient: SignalClient, ioDispatcher: CoroutineDispatcher, defaultDispatcher: CoroutineDispatcher)
    sid: Participant.Sid
    identity: Participant.Identity? (nullable, default null)
    signalClient: SignalClient
    ioDispatcher: CoroutineDispatcher
    defaultDispatcher: CoroutineDispatcher
```

----------------------------------------

TITLE: Registering Participant Connected Event Listener in Python
DESCRIPTION: This Python example demonstrates how to register a callback function to handle the 'participant_connected' event in a LiveKit room, printing the identity of the newly connected participant. It shows the basic syntax for using the `room.on()` method.

SOURCE: https://docs.livekit.io/reference/python/livekit/rtc/room

LANGUAGE: python
CODE:
```
def on_participant_connected(participant):
    print(f"Participant connected: {participant.identity}")

room.on("participant_connected", on_participant_connected)
```

----------------------------------------

TITLE: Handle Participant Connected Event
DESCRIPTION: An internal method called when a participant connects to the room. It links the participant if human input is not already set.

SOURCE: https://docs.livekit.io/reference/python/livekit/agents/voice_assistant/index

LANGUAGE: APIDOC
CODE:
```
def _on_participant_connected(self, participant: rtc.RemoteParticipant):
```

----------------------------------------

TITLE: Process LiveKit Room and Participant Events in Python
DESCRIPTION: This Python code snippet illustrates the dispatching and handling of various LiveKit SDK events. It includes logic for events such as track subscription failures, track muting/unmuting, changes in active speakers, updates to room and participant metadata/names/attributes, and connection quality changes. For each event, it retrieves relevant participant and track information and emits a corresponding custom event.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/rtc/index

LANGUAGE: python
CODE:
```
            elif which == "track_subscription_failed":
                identity = event.track_subscription_failed.participant_identity
                rparticipant = self._remote_participants[identity]
                error = event.track_subscription_failed.error
                self.emit(
                    "track_subscription_failed",
                    rparticipant,
                    event.track_subscription_failed.track_sid,
                    error,
                )
            elif which == "track_muted":
                identity = event.track_muted.participant_identity
                # TODO: pass participant identity
                participant = self._retrieve_participant(identity)
                assert isinstance(participant, Participant)
                publication = participant.track_publications[event.track_muted.track_sid]
                publication._info.muted = True
                if publication.track:
                    publication.track._info.muted = True

                self.emit("track_muted", participant, publication)
            elif which == "track_unmuted":
                identity = event.track_unmuted.participant_identity
                # TODO: pass participant identity
                participant = self._retrieve_participant(identity)
                assert isinstance(participant, Participant)
                publication = participant.track_publications[event.track_unmuted.track_sid]
                publication._info.muted = False
                if publication.track:
                    publication.track._info.muted = False

                self.emit("track_unmuted", participant, publication)
            elif which == "active_speakers_changed":
                speakers: list[Participant] = []
                # TODO: pass participant identity
                for identity in event.active_speakers_changed.participant_identities:
                    participant = self._retrieve_participant(identity)
                    assert isinstance(participant, Participant)
                    speakers.append(participant)

                self.emit("active_speakers_changed", speakers)
            elif which == "room_metadata_changed":
                old_metadata = self.metadata
                self._info.metadata = event.room_metadata_changed.metadata
                self.emit("room_metadata_changed", old_metadata, self.metadata)
            elif which == "room_sid_changed":
                if not self._info.sid:
                    self._first_sid_future.set_result(event.room_sid_changed.sid)
                self._info.sid = event.room_sid_changed.sid
                # This is an internal event, not exposed to users
            elif which == "participant_metadata_changed":
                identity = event.participant_metadata_changed.participant_identity
                # TODO: pass participant identity
                participant = self._retrieve_participant(identity)
                assert isinstance(participant, Participant)
                old_metadata = participant.metadata
                participant._info.metadata = event.participant_metadata_changed.metadata
                self.emit(
                    "participant_metadata_changed",
                    participant,
                    old_metadata,
                    participant.metadata,
                )
            elif which == "participant_name_changed":
                identity = event.participant_name_changed.participant_identity
                participant = self._retrieve_participant(identity)
                assert isinstance(participant, Participant)
                old_name = participant.name
                participant._info.name = event.participant_name_changed.name
                self.emit("participant_name_changed", participant, old_name, participant.name)
            elif which == "participant_attributes_changed":
                identity = event.participant_attributes_changed.participant_identity
                attributes = event.participant_attributes_changed.attributes
                changed_attributes = dict(
                    (entry.key, entry.value)
                    for entry in event.participant_attributes_changed.changed_attributes
                )
                participant = self._retrieve_participant(identity)
                assert isinstance(participant, Participant)
                participant._info.attributes.clear()
                participant._info.attributes.update((entry.key, entry.value) for entry in attributes)
                self.emit(
                    "participant_attributes_changed",
                    changed_attributes,
                    participant,
                )
            elif which == "connection_quality_changed":
                identity = event.connection_quality_changed.participant_identity
                # TODO: pass participant identity
                participant = self._retrieve_participant(identity)
                self.emit(
```

----------------------------------------

TITLE: LiveKit Room Internal Data Stream and Participant Management
DESCRIPTION: Internal methods of the LiveKit `Room` class for processing incoming data stream chunks and trailers, draining asynchronous tasks, retrieving and creating participant objects, and providing a string representation of the room.

SOURCE: https://docs.livekit.io/reference/python/v1/livekit/rtc/room

LANGUAGE: Python
CODE:
```
                byte_stream_handler(byte_reader, participant_identity)
            else:
                logging.warning("received unknown header type, %s", stream_type)
            pass

        async def _handle_stream_chunk(self, chunk: proto_room.DataStream.Chunk):
            text_reader = self._text_stream_readers.get(chunk.stream_id)
            file_reader = self._byte_stream_readers.get(chunk.stream_id)

            if text_reader:
                await text_reader._on_chunk_update(chunk)
            elif file_reader:
                await file_reader._on_chunk_update(chunk)

        async def _handle_stream_trailer(self, trailer: proto_room.DataStream.Trailer):
            text_reader = self._text_stream_readers.get(trailer.stream_id)
            file_reader = self._byte_stream_readers.get(trailer.stream_id)

            if text_reader:
                await text_reader._on_stream_close(trailer)
                self._text_stream_readers.pop(trailer.stream_id)
            elif file_reader:
                await file_reader._on_stream_close(trailer)
                self._byte_stream_readers.pop(trailer.stream_id)

        async def _drain_rpc_invocation_tasks(self) -> None:
            if self._rpc_invocation_tasks:
                for task in self._rpc_invocation_tasks:
                    task.cancel()
                await asyncio.gather(*self._rpc_invocation_tasks, return_exceptions=True)

        async def _drain_data_stream_tasks(self) -> None:
            if self._data_stream_tasks:
                for task in self._data_stream_tasks:
                    task.cancel()
                await asyncio.gather(*self._data_stream_tasks, return_exceptions=True)

        def _retrieve_remote_participant(self, identity: str) -> Optional[RemoteParticipant]:
            """Retrieve a remote participant by identity"""
            return self._remote_participants.get(identity, None)

        def _retrieve_participant(self, identity: str) -> Optional[Participant]:
            """Retrieve a local or remote participant by identity"""
            if identity and identity == self.local_participant.identity:
                return self.local_participant

            return self._retrieve_remote_participant(identity)

        def _create_remote_participant(
            self, owned_info: proto_participant.OwnedParticipant
        ) -> RemoteParticipant:
            if owned_info.info.identity in self._remote_participants:
                raise Exception("participant already exists")

            participant = RemoteParticipant(owned_info)
            self._remote_participants[participant.identity] = participant
            return participant

        def __repr__(self) -> str:
            sid = "unknown"
            if self._first_sid_future.done():
                sid = self._first_sid_future.result()

            return f"rtc.Room(sid={sid}, name={self.name}, metadata={self.metadata}, connection_state={ConnectionState.Name(self._connection_state)})"
```

----------------------------------------

TITLE: Implement LiveKit Agent Room Connection
DESCRIPTION: Connects the LiveKit agent to a specified room using provided URL and token. It initializes room options including E2EE, auto-subscribe, and RTC configuration, then connects and handles initial participant availability.

SOURCE: https://docs.livekit.io/reference/python/livekit/agents/index

LANGUAGE: python
CODE:
```
async def connect(
    self,
    *,
    e2ee: rtc.E2EEOptions | None = None,
    auto_subscribe: AutoSubscribe = AutoSubscribe.SUBSCRIBE_ALL,
    rtc_config: rtc.RtcConfiguration | None = None,
) -> None:
    """Connect to the room. This method should be called only once.

    Args:
        e2ee: End-to-end encryption options. If provided, the Agent will utilize end-to-end encryption. Note: clients will also need to handle E2EE.
        auto_subscribe: Whether to automatically subscribe to tracks. Default is AutoSubscribe.SUBSCRIBE_ALL.
        rtc_config: Custom RTC configuration to use when connecting to the room.
    """
    room_options = rtc.RoomOptions(
        e2ee=e2ee,
        auto_subscribe=auto_subscribe == AutoSubscribe.SUBSCRIBE_ALL,
        rtc_config=rtc_config,
    )

    await self._room.connect(self._info.url, self._info.token, options=room_options)
    self._on_connect()
    for p in self._room.remote_participants.values():
        self._participant_available(p)

    _apply_auto_subscribe_opts(self._room, auto_subscribe)
```