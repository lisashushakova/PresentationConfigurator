let selectedPres = null
let selectedSlide = null

const slideTagsDropList = new customDropList(
    document.querySelector('#slideTagsDropList'),
    console.log
)

const presDrawer = new presentationDrawer(
document.querySelector('.pres-drawer'),
async (slide) => {
    selectedSlide = slide
    slide.tags.forEach(tag => {
      if (tag.tagValue != null)
          tag.displayString = `${tag.tagName} (${tag.tagValue})`
      else
          tag.displayString = `${tag.tagName}`
    })
    slideTagsDropList.loadList(slide.tags, 'displayString')
}
)

const presDropList = new customDropList(
    document.querySelector('#presDropList'),
    async (pres) => {
        presDrawer.drawerElement.classList.add('loading')
        selectedSlide = null
        const slides = await fetch('http://localhost:8000/presentations/slides?' + new URLSearchParams({
            pres_id: pres.presId
        }))
        selectedPres = pres
        presDrawer.draw(slides)
        presDrawer.drawerElement.classList.remove('loading')
    }
)

presDropList.listBodyElement.classList.add('loading')
const presList = await fetch()
presDropList.loadList(presList, 'presName')
presDropList.listBodyElement.classList.remove('loading')





document.querySelector('#addPresBtn').addEventListener('click', async () => {
const pres = await new Promise(r => {
  google.script.run.withSuccessHandler(r).createPres(presDropList.input.value)
})
presDropList.loadList([...presDropList.contentList, pres], 'presName')
})

document.querySelector('#addTagBtn').addEventListener('click', async () => {
slideTagsDropList.listBodyElement.classList.add('loading')
let [tagName, tagValue] = slideTagsDropList.input.value.split('=')
if (!tagValue) tagValue = null
const link = await new Promise(r => {
  google.script.run.withSuccessHandler(r).linkSlideWithTag(selectedSlide.slideId, tagName, tagValue)
})

let displayString
if (link.value != null)
  displayString = `${link.tagName} (${link.value})`
else
  displayString = `${link.tagName}`
const tagObject = {'tagId': link.tagId, 'tagName': link.tagName, 'tagValue': link.value, 'displayString': displayString}
slideTagsDropList.loadList([...slideTagsDropList.contentList, tagObject], 'displayString')
for (const slide of presDrawer.slides) {
  if (slide.slideId == link.slideId) {
    console.log(slide, link)
    slide.tags.push(tagObject)
    break
  }

}

slideTagsDropList.listBodyElement.classList.remove('loading')

})


document.querySelector('#delTagBtn').addEventListener('click', async () => {
slideTagsDropList.listBodyElement.classList.add('loading')
const tagName = slideTagsDropList.input.value
const pres = await new Promise(r => {
  google.script.run.withSuccessHandler(r).unlinkSlideFromTag(selectedSlide.slideId, tagName)
})
console.log("1:", presDrawer.slides)
for (const [i, slide] of Object.entries(presDrawer.slides)) {
  if (slide.slideId == selectedSlide.slideId) {
    for (const [j, tag] of Object.entries(slide.tags)) {
      if (tag.tagName == tagName) {
        presDrawer.slides[i].tags.splice(j, 1)
      }
    }
  }
}

slideTagsDropList.loadList(slideTagsDropList.contentList)
console.log("2:", presDrawer.slides)
const listHtmlElement = slideTagsDropList.listBodyElement
const listContentHtml = listHtmlElement.querySelector('.custom-drop-list-content')
for (const child of listContentHtml.children) {
  if (child.innerHTML == 'undefined') child.remove()
}
slideTagsDropList.listBodyElement.classList.remove('loading')
})

document.querySelector('#importSlidesBtn').addEventListener('click', () => {
const modal = document.querySelector('.slides-sources-modal')
modal.classList.add('visible')
})

let selectedSlides

document.querySelector('#findImportBtn').addEventListener('click', async () => {
const selectedSlidesWindow = document.querySelector(".selected-slides-window")
selectedSlidesWindow.classList.add('loading')
const input = document.querySelector("#logicalExpressionInput")
selectedSlides = await new Promise(r => {
  google.script.run.withSuccessHandler(r).logicalExpression(input.value)
})

selectedSlidesWindow.innerHTML = ''
for (const slide of selectedSlides) {
  for (const pres of presList) {
    if (pres.presId == slide.parentPresId) {
      selectedSlidesWindow.innerHTML += `Презентация "${pres.presName}" слайд ${slide.index}`
    }
  }
}
selectedSlidesWindow.classList.remove('loading')
})

document.querySelector('#confirmImportBtn').addEventListener('click', async () => {
const selectedSlidesWindow = document.querySelector(".selected-slides-window")
selectedSlidesWindow.classList.add('loading')
await new Promise(r => {

  google.script.run.withSuccessHandler(r).appendSlides(selectedPres.presId, selectedSlides)
})
const modal = document.querySelector('.slides-sources-modal')
modal.classList.remove('visible')
selectedSlidesWindow.classList.remove('loading')
presDropList.listBodyElement.classList.add('loading')
const presList = await new Promise(r => {
  google.script.run.withSuccessHandler(r).getUserPresList()
})
presDropList.loadList(presList, 'presName')
presDropList.listBodyElement.classList.remove('loading')
presDrawer.draw([...presDrawer.slides, ...selectedSlides])

})

document.querySelector('#cancelImportBtn').addEventListener('click', async () => {
const modal = document.querySelector('.slides-sources-modal')
modal.classList.remove('visible')
})





