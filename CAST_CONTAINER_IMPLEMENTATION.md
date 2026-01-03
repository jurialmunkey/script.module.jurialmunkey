# Cast Container Implementation

## Overview
This document describes the implementation of cast container functionality for the script.module.jurialmunkey module, specifically addressing issue #1553 in the script.skinvariables plugin.

## Problem Statement
Skinners needed a way to populate a secondary container (typically Container(50)) with cast members from movies, TV shows, and episodes, allowing them to display cast information (name, role, thumbnail) in their skins.

## Solution
The implementation adds cast container support to the `jurialmunkey.jrpcid` module by:

1. Adding a `get_cast_items()` method to the base `ListGetItemDetails` class
2. Adding a `get_cast_directory()` method for populating containers with cast data
3. Creating three new dedicated classes for cast containers:
   - `ListGetMovieCast`
   - `ListGetTVShowCast`
   - `ListGetEpisodeCast`

## Implementation Details

### Base Class Enhancement
The `ListGetItemDetails` base class now includes two new methods:

#### `get_cast_items(dbid)`
Fetches cast information from Kodi's JSON-RPC API and creates ListItem objects for each cast member.

**Returns:** A list of tuples `(path, ListItem, is_folder)` where each ListItem contains:
- **Label:** Actor's name
- **Label2:** Character role
- **Artwork:** Thumbnail image (if available)
- **Properties:**
  - `name` - Actor's name
  - `role` - Character role
  - `order` - Cast order from database
  - `index` - Zero-based index in cast list
  - `thumbnail` - Thumbnail URL

#### `get_cast_directory(dbid, **kwargs)`
Populates a directory/container with cast member list items.

**Parameters:**
- `dbid` - Database ID of the movie/show/episode
- `**kwargs` - Additional optional parameters

**Container Content:** Set to 'actors'

### New Cast Classes

#### ListGetMovieCast
Retrieves and populates cast information for a movie.

**Usage in script.skinvariables:**
```python
from jurialmunkey.jrpcid import ListGetMovieCast

# Populate Container(50) with movie cast
ListGetMovieCast(handle=50, paramstring='').get_directory(dbid=movieid)
```

#### ListGetTVShowCast
Retrieves and populates cast information for a TV show.

**Usage in script.skinvariables:**
```python
from jurialmunkey.jrpcid import ListGetTVShowCast

# Populate Container(50) with TV show cast
ListGetTVShowCast(handle=50, paramstring='').get_directory(dbid=tvshowid)
```

#### ListGetEpisodeCast
Retrieves and populates cast information for an episode.

**Usage in script.skinvariables:**
```python
from jurialmunkey.jrpcid import ListGetEpisodeCast

# Populate Container(50) with episode cast
ListGetEpisodeCast(handle=50, paramstring='').get_directory(dbid=episodeid)
```

## Skin Integration

### Accessing Cast Data in Skin XML
Once the cast container is populated, skinners can access the data using:

```xml
<!-- Display cast member name -->
$INFO[Container(50).ListItem.Label]

<!-- Display character role -->
$INFO[Container(50).ListItem.Label2]

<!-- Display cast member thumbnail -->
$INFO[Container(50).ListItem.Art(thumb)]

<!-- Using properties -->
$INFO[Container(50).ListItem.Property(name)]
$INFO[Container(50).ListItem.Property(role)]
$INFO[Container(50).ListItem.Property(order)]
$INFO[Container(50).ListItem.Property(thumbnail)]

<!-- Number of cast members -->
$INFO[Container(50).NumItems]
```

### Example Skin List
```xml
<control type="list" id="50">
    <itemlayout width="200" height="300">
        <control type="image">
            <texture>$INFO[ListItem.Art(thumb)]</texture>
        </control>
        <control type="label">
            <label>$INFO[ListItem.Label]</label> <!-- Actor name -->
        </control>
        <control type="label">
            <label>$INFO[ListItem.Label2]</label> <!-- Role -->
        </control>
    </itemlayout>
    <focusedlayout width="200" height="300">
        <!-- Same as itemlayout with focus effects -->
    </focusedlayout>
</control>
```

## Script.skinvariables Integration

To use this functionality in script.skinvariables, the plugin needs to:

1. **Import the new classes:**
```python
from jurialmunkey.jrpcid import ListGetMovieCast, ListGetTVShowCast, ListGetEpisodeCast
```

2. **Create route handlers** (in plugin.py or appropriate router file):
```python
@router.route('movie/cast/<movieid>')
def movie_cast(movieid):
    """Route to populate cast container for a movie"""
    ListGetMovieCast(handle=ADDON_HANDLE, paramstring='').get_directory(dbid=movieid)

@router.route('tvshow/cast/<tvshowid>')
def tvshow_cast(tvshowid):
    """Route to populate cast container for a TV show"""
    ListGetTVShowCast(handle=ADDON_HANDLE, paramstring='').get_directory(dbid=tvshowid)

@router.route('episode/cast/<episodeid>')
def episode_cast(episodeid):
    """Route to populate cast container for an episode"""
    ListGetEpisodeCast(handle=ADDON_HANDLE, paramstring='').get_directory(dbid=episodeid)
```

3. **Use in skin templates:**
```xml
<!-- Example: Load movie cast into Container(50) -->
<onload>SetProperty(cast_container,plugin://script.skinvariables/movie/cast/$INFO[ListItem.DBID],50)</onload>

<!-- Or update container directly -->
<onclick>Container(50).Update(plugin://script.skinvariables/movie/cast/$INFO[ListItem.DBID])</onclick>
```

## Technical Details

### JSON-RPC Queries
The implementation uses Kodi's VideoLibrary JSON-RPC methods:
- `VideoLibrary.GetMovieDetails` with `["cast"]` properties
- `VideoLibrary.GetTVShowDetails` with `["cast"]` properties
- `VideoLibrary.GetEpisodeDetails` with `["cast"]` properties

### Cast Data Structure
Each cast member from Kodi's database contains:
```python
{
    "name": "Actor Name",
    "role": "Character Name",
    "order": 0,  # Cast order
    "thumbnail": "image://url/to/actor/thumb/"
}
```

## Performance Considerations
- Cast data is fetched directly from Kodi's database via JSON-RPC
- No external API calls are made
- Minimal processing overhead
- Container population is handled by Kodi's plugin directory mechanism

## Backward Compatibility
- This implementation adds new functionality without modifying existing behavior
- Existing `ListGetMovieDetails`, `ListGetTVShowDetails`, and `ListGetEpisodeDetails` classes remain unchanged
- No breaking changes to the API

## Future Enhancements
Possible future improvements:
1. Add filtering options (e.g., limit number of cast members)
2. Add sorting options (by name, role, order)
3. Support for crew members (directors, writers, etc.)
4. Caching of cast data for performance
5. Extended properties (actor biography, filmography count, etc.)

## Example Use Cases

### Use Case 1: Movie Cast Dialog
Display a full cast list when user clicks on a movie:
```xml
<onclick>Dialog.Close(all)</onclick>
<onclick>ActivateWindow(1111)</onclick>
<onload>Container(50).Update(plugin://script.skinvariables/movie/cast/$INFO[Window(home).Property(movie.dbid)])</onload>
```

### Use Case 2: Inline Cast Display
Show top cast members directly in the movie information screen:
```xml
<!-- Update Container(50) when focus changes -->
<onfocus>Container(50).Update(plugin://script.skinvariables/movie/cast/$INFO[ListItem.DBID])</onfocus>

<!-- Display first few cast members -->
<control type="group">
    <control type="image">
        <texture>$INFO[Container(50).ListItem(0).Art(thumb)]</texture>
    </control>
    <control type="label">
        <label>$INFO[Container(50).ListItem(0).Label]</label>
    </control>
</control>
```

### Use Case 3: Cast Grid/Wall
Create a grid view of cast members:
```xml
<control type="panel" id="50">
    <viewtype label="Cast">cast</viewtype>
    <orientation>vertical</orientation>
    <itemlayout width="200" height="300">
        <!-- Cast member card layout -->
    </itemlayout>
</control>
```

## Testing Recommendations

### Manual Testing
1. **Test with a movie that has cast data:**
   ```python
   from jurialmunkey.jrpcid import ListGetMovieCast
   ListGetMovieCast(handle=50, paramstring='').get_directory(dbid=123)
   ```

2. **Verify in Kodi skin:**
   - Check `$INFO[Container(50).NumItems]` returns correct count
   - Verify all properties are accessible
   - Confirm thumbnails load correctly

3. **Test edge cases:**
   - Movie/show with no cast data
   - Movie/show with many cast members (100+)
   - Cast members without thumbnails

### Integration Testing
1. Test with script.skinvariables routes
2. Verify container updates work correctly
3. Test with different skin container IDs
4. Verify memory usage with large cast lists

## Troubleshooting

### No Cast Members Displayed
- Verify the movie/show/episode has cast data in Kodi's database
- Check that the correct DBID is being passed
- Verify Container ID is correct (e.g., 50)
- Check Kodi logs for JSON-RPC errors

### Thumbnails Not Loading
- Verify cast members have thumbnail data in database
- Check image cache settings in Kodi
- Ensure artwork scrapers are configured

### Container Not Updating
- Verify plugin handle is correctly initialized
- Check that container exists in skin XML
- Verify route is registered correctly in plugin

## References
- [Kodi JSON-RPC API Documentation](https://kodi.wiki/view/JSON-RPC_API)
- [Kodi Container Controls](https://kodi.wiki/view/Container_Controls)
- [Kodi ListItem Properties](https://kodi.wiki/view/ListItem)
- [Script.skinvariables Repository](https://github.com/jurialmunkey/script.skinvariables)
- [Script.module.jurialmunkey Repository](https://github.com/jurialmunkey/script.module.jurialmunkey)

## Version History
- **v0.2.30** (Pending) - Added cast container functionality
  - Added `get_cast_items()` method to `ListGetItemDetails`
  - Added `get_cast_directory()` method to `ListGetItemDetails`
  - Added `ListGetMovieCast`, `ListGetTVShowCast`, and `ListGetEpisodeCast` classes
