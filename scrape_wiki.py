import requests
from bs4 import BeautifulSoup
import folium
import re
from urllib.parse import urljoin
import gpxpy
import gpxpy.gpx


# Step 1: Wikipedia page with list of mansions in Finland
base_url = "https://fi.wikipedia.org"
list_url = "https://fi.wikipedia.org/wiki/Luettelo_Suomen_kartanoista"

def get_mansion_links(list_url):
    resp = requests.get(list_url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = []

    for a in soup.select("a[href^='/wiki/']"):
        href = a['href']
        if 'kartano' in a.text or 'Kartano' in a.text or 'gård' in a.text or 'Gård' in a.text:
            links.append(urljoin(base_url, href))

    return list(set(links))  # Remove duplicates

def get_coordinates_from_page(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')

    geo = soup.find("span", class_="geo")
    if geo:
        try:
            lat, lon = map(float, geo.text.strip().split(';'))
            return lat, lon
        except ValueError:
            pass
    return None

def collect_coordinates_with_names(urls):
    coords = []
    for url in urls:
        print(f"Checking: {url}")
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Try to find coordinates
        geo = soup.find("span", class_="geo")
        if geo:
            try:
                lat, lon = map(float, geo.text.strip().split(';'))

                # Try to get the page title as name
                title_tag = soup.find("h1", id="firstHeading")
                name = title_tag.text.strip() if title_tag else "Unknown Mansion"

                coords.append((name, lat, lon))
            except ValueError:
                continue
    return coords

def plot_on_map(coords_with_names):
    m = folium.Map(location=[63.0, 26.0], zoom_start=5)
    for name, lat, lon in coords_with_names:
        folium.Marker(location=[lat, lon], popup=name).add_to(m)
    return m


def export_to_gpx(coords_with_names, filename="mansions.gpx"):
    gpx = gpxpy.gpx.GPX()

    for name, lat, lon in coords_with_names:
        waypoint = gpxpy.gpx.GPXWaypoint(latitude=lat, longitude=lon, name=name)
        gpx.waypoints.append(waypoint)

    with open(filename, "w") as f:
        f.write(gpx.to_xml())
    print(f"GPX file saved as {filename}")



# Run the steps
links = get_mansion_links(list_url)
coords = collect_coordinates_with_names(links)
map_object = plot_on_map(coords)
export_to_gpx(coords)

# Save map to HTML
map_object.save("finland_mansions_map.html")
print("Map saved to finland_mansions_map.html")
