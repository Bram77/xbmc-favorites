//Some additional Effects
Effect.PhaseIn = function(element) {
  element = $(element);
  new Effect.BlindDown(element, arguments[1] || {});
  //new Effect.Appear(element, arguments[2] || arguments[1] || {});
}

Effect.PhaseOut = function(element) {
  element = $(element);
  new Effect.Fade(element, arguments[1] || {});
  new Effect.BlindUp(element, arguments[2] || arguments[1] || {});
}

Effect.Phase = function(element) {
  element = $(element);
  if (element.style.display == 'none')
    new Effect.PhaseIn(element, arguments[1] || {}, arguments[2] || arguments[1] || {});
  else new Effect.PhaseOut(element, arguments[1] || {}, arguments[2] || arguments[1] || {});
}