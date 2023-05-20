import React, {useEffect, useRef, useState} from 'react'
import './PresentationPreviewBlock.css'

const PreviewSlideCard = (props) => {

    return (
        <div className='PreviewSlideCard' draggable
            onDragStart={() => {
                props.setDraggedSlide(props.slide)
                props.setFromIndex(props.previewIndex)
            }}
        >
            <img className={props.slide.ratio} src={'data:image/png;base64,' + props.slide.thumbnail}
                onContextMenu={(e) => {
                    e.preventDefault()
                    props.setPreviewSlides(prev => prev.filter(slide => slide.id !== props.slide.id))
                }}
            />
        </div>
    )
}

const DropPad = (props) => {

    const ref = useRef()

    return (
        <div ref={ref} className='DropPad' onDragOver={e => {
            e.preventDefault()
        }} onDrop={() => {
            props.setToIndex(props.index)
            ref.current.classList.remove('dragover')
        }} onDragEnter={() => {
            ref.current.classList.add('dragover')
        }} onDragLeave={() => {
            ref.current.classList.remove('dragover')
        }}
        >
        </div>
    )
}

const PresentationPreviewBlock = (props) => {

    const [draggedSlide, setDraggedSlide] = useState(null)
    const [fromIndex, setFromIndex] = useState(null)
    const [toIndex, setToIndex] = useState(null)

    const ref = useRef()

    const [enteredScrollUp, setEnteredScrollUp] = useState(false)
    const [enteredScrollDown, setEnteredScrollDown] = useState(false)
    const [scrollSpeedRatio, setScrollSpeedRatio] = useState(0)
    const [counter, setCounter] = useState(0)

    useEffect(() => {
        if (enteredScrollUp) {
            ref.current.scrollTop -= Math.pow(scrollSpeedRatio, 2) * scrollSpeed
            setTimeout(() => setCounter(prev => prev + 1), 10)
        }
        if (enteredScrollDown) {
            ref.current.scrollTop += Math.pow(scrollSpeedRatio, 2) * scrollSpeed
            setTimeout(() => setCounter(prev => prev + 1), 10)
        }
    }, [enteredScrollUp, enteredScrollDown, counter])

    const scrollSpeed = 40
    const scrollTolerance = 0.2

    useEffect(() => {
        if (toIndex !== null) {
            props.setPreviewSlides(prev => {
                const res = []
                if (fromIndex < toIndex) {
                    res.push(...prev.slice(0, fromIndex))
                    res.push(...prev.slice(fromIndex + 1, toIndex))
                    res.push(draggedSlide)
                    res.push(...prev.slice(toIndex, prev.length))
                } else {
                    res.push(...prev.slice(0, toIndex))
                    res.push(draggedSlide)
                    res.push(...prev.slice(toIndex, fromIndex))
                    res.push(...prev.slice(fromIndex + 1, prev.length))
                }
                setDraggedSlide(null)
                setFromIndex(null)
                setToIndex(null)
                return res
            })
        }
    }, [toIndex])

    return(
        <div className='PresentationPreviewBlock'
             onContextMenu={(e) => e.preventDefault()}
             ref={ref}
             onDragOver={e => {
                 const localPosY = e.clientY - ref.current.offsetTop
                 const scrollUpStart = 0
                 const scrollUpEnd = scrollTolerance * ref.current.clientHeight
                 const scrollDownStart = (1 - scrollTolerance) * ref.current.clientHeight
                 const scrollDownEnd = ref.current.clientHeight

                 if (localPosY < scrollUpEnd) {
                     setEnteredScrollUp(true)
                     setScrollSpeedRatio((scrollUpEnd - localPosY) / (scrollUpEnd - scrollUpStart))
                 } else if (localPosY > scrollDownStart) {
                     setEnteredScrollDown(true)
                     setScrollSpeedRatio((localPosY - scrollDownStart) / (scrollDownEnd - scrollDownStart))
                 } else {
                     setEnteredScrollUp(false)
                     setEnteredScrollDown(false)
                     setScrollSpeedRatio(0)
                 }
             }}
             onDragEnd={() => {
                setEnteredScrollUp(false)
                setEnteredScrollDown(false)
                setScrollSpeedRatio(0)
             }}
        >
            <div className='body'>
                {props.previewSlides.map((slide, previewIndex) =>
                <>
                        <DropPad index={previewIndex} setToIndex={setToIndex}/>
                        <PreviewSlideCard
                            slide={slide}
                            previewIndex={previewIndex}
                            setPreviewSlides={props.setPreviewSlides}
                            setDraggedSlide={setDraggedSlide}
                            setFromIndex={setFromIndex}
                        />
                    </>
                )}
                <DropPad index={props.previewSlides.length} setToIndex={setToIndex}/>
            </div>

            {props.previewSlides.length > 0
                ? <button onClick={() => props.setShowBuildPresentation(true)}>Собрать презентацию</button>
                : null}
        </div>
    )

}

export default PresentationPreviewBlock