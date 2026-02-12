"""
Example usage of the cast container functionality.

This file demonstrates how to use the new cast container classes
in script.module.jurialmunkey to populate containers with cast information.

NOTE: This is example code for demonstration purposes.
"""

from jurialmunkey.jrpcid import (
    ListGetMovieCast,
    ListGetTVShowCast,
    ListGetEpisodeCast,
    ListGetMovieDetails
)


def example_movie_cast():
    """
    Example: Get cast information for a movie
    
    This would typically be called from a plugin route handler.
    The handle parameter would be passed from the plugin routing system.
    """
    movie_dbid = 123  # Replace with actual movie database ID
    
    # Create an instance with plugin handle
    # In a real plugin, the handle would come from the routing system
    cast_list = ListGetMovieCast(handle=50, paramstring='')
    
    # Populate the container with cast members
    cast_list.get_directory(dbid=movie_dbid)
    
    print(f"Movie cast container populated for movie ID: {movie_dbid}")


def example_tvshow_cast():
    """
    Example: Get cast information for a TV show
    """
    tvshow_dbid = 456  # Replace with actual TV show database ID
    
    cast_list = ListGetTVShowCast(handle=50, paramstring='')
    cast_list.get_directory(dbid=tvshow_dbid)
    
    print(f"TV show cast container populated for show ID: {tvshow_dbid}")


def example_episode_cast():
    """
    Example: Get cast information for an episode
    """
    episode_dbid = 789  # Replace with actual episode database ID
    
    cast_list = ListGetEpisodeCast(handle=50, paramstring='')
    cast_list.get_directory(dbid=episode_dbid)
    
    print(f"Episode cast container populated for episode ID: {episode_dbid}")


def example_get_cast_items():
    """
    Example: Get cast items without populating a container
    
    This shows how to access the raw cast data as list items
    without immediately populating a container directory.
    """
    movie_dbid = 123
    
    cast_handler = ListGetMovieCast(handle=None, paramstring='')
    cast_items = cast_handler.get_cast_items(dbid=movie_dbid)
    
    # cast_items is a list of tuples: (path, ListItem, is_folder)
    for path, listitem, is_folder in cast_items:
        name = listitem.getLabel()
        role = listitem.getLabel2()
        thumb = listitem.getProperty('thumbnail')
        order = listitem.getProperty('order')
        
        print(f"Cast Member: {name}")
        print(f"  Role: {role}")
        print(f"  Order: {order}")
        print(f"  Thumbnail: {thumb}")
        print()


def example_combined_details_and_cast():
    """
    Example: Get both movie details and cast information
    
    This demonstrates getting the main movie details in one container
    and the cast in a secondary container.
    """
    movie_dbid = 123
    
    # Get movie details in main container (e.g., Container(9999))
    movie_details = ListGetMovieDetails(handle=9999, paramstring='')
    movie_details.get_directory(dbid=movie_dbid)
    
    # Get cast in secondary container (e.g., Container(50))
    movie_cast = ListGetMovieCast(handle=50, paramstring='')
    movie_cast.get_directory(dbid=movie_dbid)
    
    print("Movie details and cast populated in separate containers")


def example_skin_usage():
    """
    Example: How this would be used in a skin's XML
    
    This is a pseudo-example showing the skin XML patterns.
    """
    skin_xml_example = '''
    <!-- Example skin XML for using cast containers -->
    
    <!-- Method 1: Direct container update -->
    <control type="button">
        <label>Show Cast</label>
        <onclick>Container(50).Update(plugin://script.skinvariables/movie/cast/$INFO[ListItem.DBID])</onclick>
    </control>
    
    <!-- Method 2: Using SetProperty -->
    <control type="list" id="9999">
        <onfocus>SetProperty(cast_loaded,plugin://script.skinvariables/movie/cast/$INFO[ListItem.DBID],50)</onfocus>
    </control>
    
    <!-- Display cast in a list -->
    <control type="list" id="50">
        <itemlayout width="200" height="300">
            <!-- Cast member thumbnail -->
            <control type="image">
                <texture>$INFO[ListItem.Art(thumb)]</texture>
                <width>150</width>
                <height>225</height>
            </control>
            
            <!-- Actor name -->
            <control type="label">
                <label>$INFO[ListItem.Label]</label>
                <font>font13</font>
            </control>
            
            <!-- Character role -->
            <control type="label">
                <label>$INFO[ListItem.Label2]</label>
                <font>font12</font>
                <textcolor>grey</textcolor>
            </control>
        </itemlayout>
        
        <focusedlayout width="200" height="300">
            <!-- Same as itemlayout but with focus effects -->
        </focusedlayout>
    </control>
    
    <!-- Accessing cast properties -->
    <control type="label">
        <label>Actor: $INFO[Container(50).ListItem.Property(name)]</label>
    </control>
    
    <control type="label">
        <label>Role: $INFO[Container(50).ListItem.Property(role)]</label>
    </control>
    
    <control type="label">
        <label>Cast Count: $INFO[Container(50).NumItems]</label>
    </control>
    
    <!-- Looping through cast members -->
    <control type="label">
        <label>$INFO[Container(50).ListItem(0).Label]</label>
    </control>
    <control type="label">
        <label>$INFO[Container(50).ListItem(1).Label]</label>
    </control>
    <control type="label">
        <label>$INFO[Container(50).ListItem(2).Label]</label>
    </control>
    '''
    
    return skin_xml_example


def example_plugin_route():
    """
    Example: How this would be implemented in a plugin routing system
    
    This shows how script.skinvariables could add routes for cast containers.
    """
    plugin_route_example = '''
    # In the plugin's routing file (e.g., plugin.py or routes.py)
    
    from jurialmunkey.jrpcid import (
        ListGetMovieCast,
        ListGetTVShowCast,
        ListGetEpisodeCast
    )
    
    @plugin.route('/movie/cast/<movieid>')
    def route_movie_cast(movieid):
        """
        Route: plugin://script.skinvariables/movie/cast/{movieid}
        Populates container with cast for specified movie
        """
        ListGetMovieCast(
            handle=plugin.handle,
            paramstring=plugin.paramstring
        ).get_directory(dbid=int(movieid))
    
    @plugin.route('/tvshow/cast/<tvshowid>')
    def route_tvshow_cast(tvshowid):
        """
        Route: plugin://script.skinvariables/tvshow/cast/{tvshowid}
        Populates container with cast for specified TV show
        """
        ListGetTVShowCast(
            handle=plugin.handle,
            paramstring=plugin.paramstring
        ).get_directory(dbid=int(tvshowid))
    
    @plugin.route('/episode/cast/<episodeid>')
    def route_episode_cast(episodeid):
        """
        Route: plugin://script.skinvariables/episode/cast/{episodeid}
        Populates container with cast for specified episode
        """
        ListGetEpisodeCast(
            handle=plugin.handle,
            paramstring=plugin.paramstring
        ).get_directory(dbid=int(episodeid))
    '''
    
    return plugin_route_example


if __name__ == '__main__':
    """
    Note: These examples won't actually work in standalone mode
    as they require a running Kodi instance and proper plugin context.
    
    They are provided for reference and documentation purposes.
    """
    print("Cast Container Implementation Examples")
    print("=" * 50)
    print()
    print("These examples demonstrate the usage patterns for")
    print("the new cast container functionality.")
    print()
    print("Skin XML Example:")
    print(example_skin_usage())
    print()
    print("Plugin Route Example:")
    print(example_plugin_route())
