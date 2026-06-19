(function renderSketchMap() {
    const root = document.getElementById("map-root");
    const payloadNode = document.getElementById("map-payload");
    if (!root || !payloadNode) {
        return;
    }

    let payload = {};
    try {
        payload = JSON.parse(payloadNode.textContent || "{}");
    } catch (_error) {
        payload = {};
    }

    const mapStyle = isObject(payload.map_style) ? payload.map_style : {};
    const outlineColor = asColor(mapStyle.outline_color, "#66BB6A");
    const backgroundColor = asColor(mapStyle.background_color, "#FFFFFF");
    const markerColor = asColor(mapStyle.marker_color, "#E02424");
    const dotted = mapStyle.connector_style === "dotted";

    const svgNs = "http://www.w3.org/2000/svg";
    const width = 960;
    const height = 520;
    const padX = 20;
    const padY = 20;

    const svg = document.createElementNS(svgNs, "svg");
    svg.setAttribute("class", "sketch-map");
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", "Sketch map with connected locations");

    const background = document.createElementNS(svgNs, "rect");
    background.setAttribute("x", "0");
    background.setAttribute("y", "0");
    background.setAttribute("width", String(width));
    background.setAttribute("height", String(height));
    background.setAttribute("fill", backgroundColor);
    svg.appendChild(background);

    const worldOutline = document.createElementNS(svgNs, "path");
    worldOutline.setAttribute(
        "d",
        "M55 210 C130 150, 250 120, 350 170 C410 200, 465 205, 525 185 C585 165, 665 175, 725 220 C770 255, 835 285, 895 255 " +
        "M65 300 C120 330, 190 342, 252 318 C322 292, 390 292, 455 322 C525 354, 590 354, 657 323 C720 292, 790 283, 875 315 " +
        "M165 360 C200 390, 245 405, 300 389 M600 370 C652 400, 715 402, 768 372"
    );
    worldOutline.setAttribute("class", "sketch-outline");
    worldOutline.setAttribute("fill", "none");
    worldOutline.setAttribute("stroke", outlineColor);
    worldOutline.setAttribute("stroke-width", "3");
    worldOutline.setAttribute("stroke-linecap", "round");
    worldOutline.setAttribute("stroke-linejoin", "round");
    svg.appendChild(worldOutline);

    const locations = normalizeLocations(payload.locations, width, height, padX, padY);
    const locationById = new Map(locations.map((location) => [location.id, location]));

    if (Array.isArray(payload.connections)) {
        payload.connections.forEach((connection) => {
            if (!isObject(connection)) {
                return;
            }

            const fromId = asText(connection.from_id);
            const toId = asText(connection.to_id);
            if (!fromId || !toId) {
                return;
            }

            const fromLocation = locationById.get(fromId);
            const toLocation = locationById.get(toId);
            if (!fromLocation || !toLocation) {
                return;
            }

            const connector = document.createElementNS(svgNs, "line");
            connector.setAttribute("x1", String(fromLocation.x));
            connector.setAttribute("y1", String(fromLocation.y));
            connector.setAttribute("x2", String(toLocation.x));
            connector.setAttribute("y2", String(toLocation.y));
            connector.setAttribute("class", "map-connector");
            connector.setAttribute("stroke", outlineColor);
            connector.setAttribute("stroke-width", "2");
            connector.setAttribute("stroke-linecap", "round");
            if (dotted) {
                connector.setAttribute("stroke-dasharray", "3 7");
            }
            svg.appendChild(connector);
        });
    }

    locations.forEach((location) => {
        const marker = document.createElementNS(svgNs, "circle");
        marker.setAttribute("cx", String(location.x));
        marker.setAttribute("cy", String(location.y));
        marker.setAttribute("r", "5");
        marker.setAttribute("class", "map-marker");
        marker.setAttribute("fill", markerColor);
        marker.setAttribute("stroke", "#FFFFFF");
        marker.setAttribute("stroke-width", "1.5");

        const title = document.createElementNS(svgNs, "title");
        title.textContent = `${location.name}, ${location.country} - ${location.note}`;
        marker.appendChild(title);
        svg.appendChild(marker);

        const label = document.createElementNS(svgNs, "text");
        label.setAttribute("x", String(location.x + 8));
        label.setAttribute("y", String(location.y - 8));
        label.setAttribute("class", "map-label");
        label.textContent = location.label || location.name;
        svg.appendChild(label);

        if (location.note) {
            const note = document.createElementNS(svgNs, "text");
            note.setAttribute("x", String(location.x + 8));
            note.setAttribute("y", String(location.y + 9));
            note.setAttribute("class", "map-note");
            note.textContent = location.note;
            svg.appendChild(note);
        }
    });

    if (!locations.length) {
        const empty = document.createElementNS(svgNs, "text");
        empty.setAttribute("x", "40");
        empty.setAttribute("y", "70");
        empty.setAttribute("class", "map-note");
        empty.textContent = "No valid map locations available.";
        svg.appendChild(empty);
    }

    root.replaceChildren(svg);

    function normalizeLocations(rawLocations, canvasWidth, canvasHeight, xPad, yPad) {
        if (!Array.isArray(rawLocations)) {
            return [];
        }

        return rawLocations
            .map((entry) => {
                if (!isObject(entry)) {
                    return null;
                }

                const id = asText(entry.id);
                const name = asText(entry.name);
                const country = asText(entry.country);
                const lat = asNumber(entry.lat);
                const lng = asNumber(entry.lng);

                if (!id || !name || !country || lat === null || lng === null) {
                    return null;
                }

                const x = xPad + ((lng + 180) / 360) * (canvasWidth - xPad * 2);
                const y = yPad + ((90 - lat) / 180) * (canvasHeight - yPad * 2);

                return {
                    id,
                    name,
                    country,
                    label: asText(entry.label) || name,
                    note: asText(entry.note),
                    x: clamp(x, xPad, canvasWidth - xPad),
                    y: clamp(y, yPad, canvasHeight - yPad),
                };
            })
            .filter(Boolean);
    }

    function asText(value) {
        return typeof value === "string" ? value.trim() : "";
    }

    function asColor(value, fallback) {
        const color = asText(value);
        return color || fallback;
    }

    function asNumber(value) {
        if (typeof value === "number" && Number.isFinite(value)) {
            return value;
        }
        return null;
    }

    function isObject(value) {
        return value !== null && typeof value === "object" && !Array.isArray(value);
    }

    function clamp(value, min, max) {
        return Math.min(Math.max(value, min), max);
    }
})();
