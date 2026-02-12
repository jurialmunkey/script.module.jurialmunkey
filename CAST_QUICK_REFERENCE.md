# Cast Container Quick Reference

## For script.skinvariables Developers

### 1. Import the Classes
```python
from jurialmunkey.jrpcid import ListGetMovieCast, ListGetTVShowCast, ListGetEpisodeCast
```

### 2. Add Routes
```python
@router.route('movie/cast/<movieid>')
def movie_cast(movieid):
    ListGetMovieCast(handle=HANDLE, paramstring='').get_directory(dbid=int(movieid))

@router.route('tvshow/cast/<tvshowid>')
def tvshow_cast(tvshowid):
    ListGetTVShowCast(handle=HANDLE, paramstring='').get_directory(dbid=int(tvshowid))

@router.route('episode/cast/<episodeid>')
def episode_cast(episodeid):
    ListGetEpisodeCast(handle=HANDLE, paramstring='').get_directory(dbid=int(episodeid))
```

### 3. That's It!
Skinners can now use:
```xml
<onclick>Container(50).Update(plugin://script.skinvariables/movie/cast/$INFO[ListItem.DBID])</onclick>
```

---

## For Kodi Skin Developers

### Basic Usage
```xml
<!-- Load cast into Container(50) -->
<onclick>Container(50).Update(plugin://script.skinvariables/movie/cast/$INFO[ListItem.DBID])</onclick>
```

### Display Cast Member Info
```xml
<!-- Actor Name -->
$INFO[Container(50).ListItem.Label]

<!-- Character Role -->
$INFO[Container(50).ListItem.Label2]

<!-- Thumbnail -->
$INFO[Container(50).ListItem.Art(thumb)]

<!-- Number of Cast Members -->
$INFO[Container(50).NumItems]
```

### Cast List Control
```xml
<control type="list" id="50">
    <itemlayout width="200" height="300">
        <control type="image">
            <texture>$INFO[ListItem.Art(thumb)]</texture>
        </control>
        <control type="label">
            <label>$INFO[ListItem.Label]</label>
        </control>
        <control type="label">
            <label>$INFO[ListItem.Label2]</label>
        </control>
    </itemlayout>
</control>
```

### Display Specific Cast Members
```xml
<!-- First cast member -->
$INFO[Container(50).ListItem(0).Label]

<!-- Second cast member -->
$INFO[Container(50).ListItem(1).Label]

<!-- Third cast member -->
$INFO[Container(50).ListItem(2).Label]
```

### Available Properties
- `ListItem.Label` - Actor name
- `ListItem.Label2` - Character role
- `ListItem.Art(thumb)` - Actor thumbnail
- `ListItem.Property(name)` - Actor name (alternative)
- `ListItem.Property(role)` - Character role (alternative)
- `ListItem.Property(order)` - Cast order from database
- `ListItem.Property(index)` - Zero-based index
- `ListItem.Property(thumbnail)` - Thumbnail URL

---

## Common Use Cases

### Show Cast on Focus
```xml
<control type="list" id="9999">
    <onfocus>Container(50).Update(plugin://script.skinvariables/movie/cast/$INFO[ListItem.DBID])</onfocus>
</control>
```

### Show Cast in Dialog
```xml
<onclick>ActivateWindow(1111)</onclick>
<onload>Container(50).Update(plugin://script.skinvariables/movie/cast/$INFO[Window(home).Property(movie.dbid)])</onload>
```

### Cast Grid View
```xml
<control type="panel" id="50">
    <orientation>vertical</orientation>
    <itemlayout width="150" height="225">
        <!-- Cast member card -->
    </itemlayout>
</control>
```

### Display First 5 Cast Members
```xml
<control type="group">
    <control type="image">
        <texture>$INFO[Container(50).ListItem(0).Art(thumb)]</texture>
    </control>
    <control type="image">
        <texture>$INFO[Container(50).ListItem(1).Art(thumb)]</texture>
    </control>
    <control type="image">
        <texture>$INFO[Container(50).ListItem(2).Art(thumb)]</texture>
    </control>
    <control type="image">
        <texture>$INFO[Container(50).ListItem(3).Art(thumb)]</texture>
    </control>
    <control type="image">
        <texture>$INFO[Container(50).ListItem(4).Art(thumb)]</texture>
    </control>
</control>
```

---

## Troubleshooting

### No Cast Displayed
- Verify movie/show has cast data in Kodi database
- Check correct DBID is being used
- Ensure Container(50) exists in skin XML

### Thumbnails Missing
- Check artwork scrapers are enabled
- Verify image cache is working
- Some cast members may not have thumbnails

### Container Not Updating
- Verify plugin route is registered
- Check Kodi log for errors
- Ensure script.skinvariables is running

---

## Route URLs

**Movies:**
```
plugin://script.skinvariables/movie/cast/{movieid}
```

**TV Shows:**
```
plugin://script.skinvariables/tvshow/cast/{tvshowid}
```

**Episodes:**
```
plugin://script.skinvariables/episode/cast/{episodeid}
```

---

## Notes

- Cast data comes from Kodi's local database (fast, no API calls)
- Container ID can be any valid container (50 is just an example)
- Works with all content types that have cast (movies, shows, episodes)
- No additional dependencies required
- Backward compatible with existing code
