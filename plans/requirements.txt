Functional requirements:
- Play songs added into the database
- Create playlists
- Create account and log in. Authentication required to use application. SendGrid for confirmation email?
- Add songs/MP3s by uploading them - use media hosting site to serve content e.g. Cloudinary. Create agnostic FileUpload code 
- Profile avatar? Use third-party to serve (see above).
- Token-based authentication (JWT tokens)
- Delete songs and playlists.
- Deploy site with Render or other free deployment platform. 
- Password reset functionality (using SendGrid for email)
- Account edit page (initiate Password reset, edit profile avatar for example)
- Pagination of songs to support scalability (server-side pagination).
- Search and sort (sort by Artist, Duration, Date Added)
- Audit trail: play history (Log every time a user plays a song. (Timestamp, UserID, SongID))
Not in scope:
- Admin dashboard/admin role. Users are admins of their own music and can CRUD.

Non-functional requirements:
- Three-layer architecture - TS React frontend, Django (Python) middleware, PostGreSQL backend DB
- Modular and maintainable API design
- Secure authentication, protected endpoints (cannot access main site without login)
- Modular frontend design (Separation of concerns, components)
- Server-side validation 
- Basic scalability consideration

BDD will help me test behavioural flow. 
TDD ensures I stick to the functional requirements.
ts-audio library simplifies music control.
