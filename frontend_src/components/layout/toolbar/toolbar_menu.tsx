/**
 * ToolBox Overlay Menu and Menu-Open Button.
 */

import { createSignal, For, onMount, Setter, splitProps } from "solid-js";
import { TOOL_CREATION_MAP, TOOL_FUNC_MAP } from "../../../src/charting_frame/tools";
import { Icon, icons } from "../../icons";
import { MenuItem, ShowMenuButton } from "../../simple_menu";
import { location_reference, overlay_div_props, OverlayCTX, OverlayDiv, point } from "../overlay_manager";
import { ToolBoxCTX } from "./toolbar";

export interface toolbar_menu_props{
    id:string
    tools:icons[][]
    default_icon:icons
}

/**
 * A single container Button to be displayed within the Toolbar. Placing the 
 * Button within the Tool-Bar automatically generates a button to open a menu
 * and display the tools given within the props.
 * 
 * Each Tool is keyed to it's respective svg icon.
 */
export function ToolBarMenuButton(props:toolbar_menu_props){
    let el = document.createElement('div')

    const [location, setLocation] = createSignal<point>({x:0, y:0})
    const [iconDeact, seticonDeact] = createSignal<icons>(icons.blank)
    const [displayIcon, setDisplayIcon] = createSignal<icons>(props.default_icon)

    const updateLocation = () => {
        setLocation({
            x: el.getBoundingClientRect().right, 
            y: el.getBoundingClientRect().top
        })
    }

    OverlayCTX().attachOverlay(
        props.id,
        <ToolBarOverlay 
            id={props.id} 
            location={location()}
            updateLocation={updateLocation}
            tools={props.tools}
            setIcon={setDisplayIcon}
        />
    )

    return (
        <div ref={el}
            class='toolbar_container'  
            onMouseEnter={() => seticonDeact(icons.menu_arrow_ew)} 
            onMouseLeave={() => seticonDeact(icons.blank)}
        >
            <Icon
                icon={displayIcon()}
                attr:active={TOOL_CREATION_MAP.get(displayIcon())?.[0]() ? "" : undefined}
                onClick={TOOL_FUNC_MAP.get(displayIcon())}
                classList={{toolbar_icon_btn:true}}
            />
            <ShowMenuButton 
                id={props.id}
                classList={{toolbar_menu_button:true}}
                icon_act={icons.menu_arrow_we}
                icon_deact={iconDeact()}
            />
        </div>
    )
}


interface toolbar_overlay_props extends Omit<overlay_div_props, "location_ref"> {
    id:string
    tools:icons[][]
    location:point
    setIcon:Setter<icons>
}
/**
 * Overlay Menu showing the available tool options within this menu. 
 * @param props.tools : 2D-Array. The first array holds all of the menu groups
 *                      Each sub-Array holds the tools within each group
 */
function ToolBarOverlay(props:toolbar_overlay_props){
    let setDisplay: Setter<boolean>
    const tools = ToolBoxCTX().tools
    const setTools = ToolBoxCTX().setTools
    const [,overlayDivProps] = splitProps(props, ["tools", "setIcon"])

    
    function addFavorite(tool:icons){
        if (!tools().includes(tool)) setTools([...tools(), tool])
    }
    function removeFavorite(tool:icons){
        if (tools().includes(tool)) setTools(tools().filter((fav) => fav != tool))
    }
    function onSel(tool:icons){
        props.setIcon(tool)
        const tool_func = TOOL_FUNC_MAP.get(tool)
        if (tool_func) tool_func()
        else console.log("invalid tool")
        setDisplay(false)
    }

    onMount(()=>{setDisplay = OverlayCTX().getDisplaySetter(props.id)})

    return (
        <OverlayDiv 
            {...overlayDivProps}
            location_ref={location_reference.TOP_LEFT}
        >
            <For each={props.tools}>{(tools_sublist) => <>

                <div class='menu_section_titlebox'/>
                <For each={tools_sublist}>{(tool)=>
                    <MenuItem
                        expand={true}
                        icon={tool}
                        label={TOOL_LABEL_MAP.get(tool)??""}
                        onSel={()=>onSel(tool)}

                        star={tools().includes(tool)}
                        starAct={() => addFavorite(tool)}
                        starDeact={() => removeFavorite(tool)}
                        starStyle={{width:'20px', height:'20px'}}
                    />
                }</For>
            </>
            }</For>
        </OverlayDiv>
    )
}

const TOOL_LABEL_MAP = new Map<icons, string>([
    [icons.cursor_cross, "Cross"],
    [icons.cursor_dot, "Dot"],
    [icons.cursor_arrow, "Arrow"],
    [icons.cursor_erase, "Erase"],

    [icons.trend_line, "Trend Line"],
    [icons.horiz_ray, "Horiz. Ray"],
    [icons.horiz_line, "Horiz. Line"],
    [icons.vert_line, "Vert. Line"],
    [icons.polyline, "Polyline"],
    [icons.channel_parallel, "Parallel Channel"], 
    [icons.channel_disjoint, "Disjoint Channel"],
    
    [icons.fib_retrace, "Fib. Retrace"], 
    [icons.fib_extend, "Fib. Extention"],

    [icons.range_price, "Price Range"], 
    [icons.range_date, "Date Range"], 
    [icons.range_price_date, "Price & Date Range"],
    // [icons., ""],
])



