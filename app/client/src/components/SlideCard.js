import React from 'react'
import './SlideCard.css'
import {useEffect, useRef} from "react";

const SlideRatio = {
    WIDESCREEN_16_TO_9: 'WIDESCREEN_16_TO_9',
    STANDARD_4_TO_3: 'STANDARD_4_TO_3'
}

const SlideCard = (props) => {
    let className = null
    let imgSrc = 'data:image/png;base64,' + props.slide.thumbnail

    const ref = useRef()

    switch (props.slide.ratio[0]) {
        case SlideRatio.WIDESCREEN_16_TO_9:
            className = 'slide-card-16-9'
            break
        case SlideRatio.STANDARD_4_TO_3:
            className = 'slide-card-4-3'
            break
    }

    if (props.expand) {
        className += ' expanded'
    }

    useEffect(() => {
        if (props.selectedSlide !== props.slide) {
            ref.current.classList.remove('selected')
        }

    }, [props.selectedSlide])

    return (
        <div ref={ref} className={'SlideCard ' + className} onClick={() => {
            if (!(props.expand)) {
                if (props.selectedSlide === props.slide) {
                props.setSelectedSlide(null)
                } else {
                    props.setSelectedSlide(props.slide)
                    ref.current.classList.add('selected')
                }
            }

        }}>
            <div className='label'>{props.expand ? null : props.slide.index + 1}</div>
            <img src={imgSrc}/>
        </div>
    )
}

export {SlideCard, SlideRatio}