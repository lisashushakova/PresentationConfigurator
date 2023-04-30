import React, {useRef, useState} from 'react'
import './SlidePoolBlock.css'

const PoolSlideCard = (props) => {

    const [selected, setSelected] = useState(false)
    const ref = useRef()

    return (
        <div className='PoolSlideCard'>
            <h5>{props.slide.label}</h5>
            <img ref={ref} className={props.slide.ratio} src={'data:image/png;base64,' + props.slide.thumbnail}
                onClick={() => {
                    if (selected) {
                        ref.current.classList.remove('selected')
                        props.setSelectedPoolSlides(prev => prev.filter(slide => slide.id !== props.slide.id))
                    } else {
                        ref.current.classList.add('selected')
                        props.setSelectedPoolSlides(prev => [...prev, props.slide])
                    }
                    setSelected(prev => !prev)
                }}
            />
        </div>
    )
}

const SlidePoolBlock = (props) => {

    return(
        <div className='SlidePoolBlock'>
            {props.poolSlides.map(slide =>
                <PoolSlideCard slide={slide} setSelectedPoolSlides={props.setSelectedPoolSlides}/>)}
        </div>
    )
}

export default SlidePoolBlock