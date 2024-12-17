(() => {
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __esm = (fn, res) => function __init() {
    return fn && (res = (0, fn[__getOwnPropNames(fn)[0]])(fn = 0)), res;
  };

  // node_modules/tslib/tslib.es6.mjs
  function __awaiter(thisArg, _arguments, P, generator) {
    function adopt(value) {
      return value instanceof P ? value : new P(function(resolve) {
        resolve(value);
      });
    }
    return new (P || (P = Promise))(function(resolve, reject) {
      function fulfilled(value) {
        try {
          step(generator.next(value));
        } catch (e) {
          reject(e);
        }
      }
      function rejected(value) {
        try {
          step(generator["throw"](value));
        } catch (e) {
          reject(e);
        }
      }
      function step(result) {
        result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected);
      }
      step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
  }
  function __generator(thisArg, body) {
    var _ = { label: 0, sent: function() {
      if (t2[0] & 1)
        throw t2[1];
      return t2[1];
    }, trys: [], ops: [] }, f2, y, t2, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() {
      return this;
    }), g;
    function verb(n) {
      return function(v) {
        return step([n, v]);
      };
    }
    function step(op) {
      if (f2)
        throw new TypeError("Generator is already executing.");
      while (g && (g = 0, op[0] && (_ = 0)), _)
        try {
          if (f2 = 1, y && (t2 = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t2 = y["return"]) && t2.call(y), 0) : y.next) && !(t2 = t2.call(y, op[1])).done)
            return t2;
          if (y = 0, t2)
            op = [op[0] & 2, t2.value];
          switch (op[0]) {
            case 0:
            case 1:
              t2 = op;
              break;
            case 4:
              _.label++;
              return { value: op[1], done: false };
            case 5:
              _.label++;
              y = op[1];
              op = [0];
              continue;
            case 7:
              op = _.ops.pop();
              _.trys.pop();
              continue;
            default:
              if (!(t2 = _.trys, t2 = t2.length > 0 && t2[t2.length - 1]) && (op[0] === 6 || op[0] === 2)) {
                _ = 0;
                continue;
              }
              if (op[0] === 3 && (!t2 || op[1] > t2[0] && op[1] < t2[3])) {
                _.label = op[1];
                break;
              }
              if (op[0] === 6 && _.label < t2[1]) {
                _.label = t2[1];
                t2 = op;
                break;
              }
              if (t2 && _.label < t2[2]) {
                _.label = t2[2];
                _.ops.push(op);
                break;
              }
              if (t2[2])
                _.ops.pop();
              _.trys.pop();
              continue;
          }
          op = body.call(thisArg, _);
        } catch (e) {
          op = [6, e];
          y = 0;
        } finally {
          f2 = t2 = 0;
        }
      if (op[0] & 5)
        throw op[1];
      return { value: op[0] ? op[1] : void 0, done: true };
    }
  }
  function __spreadArray(to, from, pack) {
    if (pack || arguments.length === 2)
      for (var i2 = 0, l = from.length, ar; i2 < l; i2++) {
        if (ar || !(i2 in from)) {
          if (!ar)
            ar = Array.prototype.slice.call(from, 0, i2);
          ar[i2] = from[i2];
        }
      }
    return to.concat(ar || Array.prototype.slice.call(from));
  }
  var init_tslib_es6 = __esm({
    "node_modules/tslib/tslib.es6.mjs"() {
    }
  });

  // node_modules/@ionic/core/dist/esm-es5/index-a5d50daf.js
  var win, doc;
  var init_index_a5d50daf = __esm({
    "node_modules/@ionic/core/dist/esm-es5/index-a5d50daf.js"() {
      win = typeof window !== "undefined" ? window : void 0;
      doc = typeof document !== "undefined" ? document : void 0;
    }
  });

  // node_modules/@ionic/core/dist/esm-es5/animation-eab5a4ca.js
  var animationPrefix, getAnimationPrefix, setStyleProperty, addClassToArray, createAnimation;
  var init_animation_eab5a4ca = __esm({
    "node_modules/@ionic/core/dist/esm-es5/animation-eab5a4ca.js"() {
      init_tslib_es6();
      init_index_a5d50daf();
      getAnimationPrefix = function(r) {
        if (animationPrefix === void 0) {
          var n = r.style.animationName !== void 0;
          var e = r.style.webkitAnimationName !== void 0;
          animationPrefix = !n && e ? "-webkit-" : "";
        }
        return animationPrefix;
      };
      setStyleProperty = function(r, n, e) {
        var i2 = n.startsWith("animation") ? getAnimationPrefix(r) : "";
        r.style.setProperty(i2 + n, e);
      };
      addClassToArray = function(r, n) {
        if (r === void 0) {
          r = [];
        }
        if (n !== void 0) {
          var e = Array.isArray(n) ? n : [n];
          return __spreadArray(__spreadArray([], r, true), e, true);
        }
        return r;
      };
      createAnimation = function(r) {
        var n;
        var e;
        var i2;
        var t2;
        var a;
        var f2;
        var u = [];
        var o = [];
        var v = [];
        var d = false;
        var c;
        var s = {};
        var l = [];
        var y = [];
        var m = {};
        var p = 0;
        var A = false;
        var g = false;
        var C;
        var b;
        var _;
        var P = true;
        var S = false;
        var T = true;
        var x;
        var E = false;
        var w = r;
        var h = [];
        var k = [];
        var R = [];
        var D = [];
        var F = [];
        var W = [];
        var I = [];
        var K = [];
        var M = [];
        var j = [];
        var q = [];
        var z = typeof AnimationEffect === "function" || win !== void 0 && typeof win.AnimationEffect === "function";
        var B = typeof Element === "function" && typeof Element.prototype.animate === "function" && z;
        var G = function() {
          return q;
        };
        var H2 = function(r2) {
          F.forEach(function(n2) {
            n2.destroy(r2);
          });
          J(r2);
          D.length = 0;
          F.length = 0;
          u.length = 0;
          V();
          d = false;
          T = true;
          return x;
        };
        var J = function(r2) {
          X();
          if (r2) {
            Y();
          }
        };
        var L = function() {
          A = false;
          g = false;
          T = true;
          C = void 0;
          b = void 0;
          _ = void 0;
          p = 0;
          S = false;
          P = true;
          E = false;
        };
        var N = function() {
          return p !== 0 && !E;
        };
        var O = function(r2, n2) {
          var e2 = n2.findIndex(function(n3) {
            return n3.c === r2;
          });
          if (e2 > -1) {
            n2.splice(e2, 1);
          }
        };
        var Q = function(r2, n2) {
          R.push({ c: r2, o: n2 });
          return x;
        };
        var U = function(r2, n2) {
          var e2 = (n2 === null || n2 === void 0 ? void 0 : n2.oneTimeCallback) ? k : h;
          e2.push({ c: r2, o: n2 });
          return x;
        };
        var V = function() {
          h.length = 0;
          k.length = 0;
          return x;
        };
        var X = function() {
          if (B) {
            q.forEach(function(r2) {
              r2.cancel();
            });
            q.length = 0;
          }
        };
        var Y = function() {
          W.forEach(function(r2) {
            if (r2 === null || r2 === void 0 ? void 0 : r2.parentNode) {
              r2.parentNode.removeChild(r2);
            }
          });
          W.length = 0;
        };
        var Z = function(r2) {
          I.push(r2);
          return x;
        };
        var $ = function(r2) {
          K.push(r2);
          return x;
        };
        var rr = function(r2) {
          M.push(r2);
          return x;
        };
        var nr = function(r2) {
          j.push(r2);
          return x;
        };
        var er = function(r2) {
          o = addClassToArray(o, r2);
          return x;
        };
        var ir = function(r2) {
          v = addClassToArray(v, r2);
          return x;
        };
        var tr = function(r2) {
          if (r2 === void 0) {
            r2 = {};
          }
          s = r2;
          return x;
        };
        var ar = function(r2) {
          if (r2 === void 0) {
            r2 = [];
          }
          for (var n2 = 0, e2 = r2; n2 < e2.length; n2++) {
            var i3 = e2[n2];
            s[i3] = "";
          }
          return x;
        };
        var fr = function(r2) {
          l = addClassToArray(l, r2);
          return x;
        };
        var ur = function(r2) {
          y = addClassToArray(y, r2);
          return x;
        };
        var or = function(r2) {
          if (r2 === void 0) {
            r2 = {};
          }
          m = r2;
          return x;
        };
        var vr = function(r2) {
          if (r2 === void 0) {
            r2 = [];
          }
          for (var n2 = 0, e2 = r2; n2 < e2.length; n2++) {
            var i3 = e2[n2];
            m[i3] = "";
          }
          return x;
        };
        var dr = function() {
          if (a !== void 0) {
            return a;
          }
          if (c) {
            return c.getFill();
          }
          return "both";
        };
        var cr = function() {
          if (C !== void 0) {
            return C;
          }
          if (f2 !== void 0) {
            return f2;
          }
          if (c) {
            return c.getDirection();
          }
          return "normal";
        };
        var sr = function() {
          if (A) {
            return "linear";
          }
          if (i2 !== void 0) {
            return i2;
          }
          if (c) {
            return c.getEasing();
          }
          return "linear";
        };
        var lr = function() {
          if (g) {
            return 0;
          }
          if (b !== void 0) {
            return b;
          }
          if (e !== void 0) {
            return e;
          }
          if (c) {
            return c.getDuration();
          }
          return 0;
        };
        var yr = function() {
          if (t2 !== void 0) {
            return t2;
          }
          if (c) {
            return c.getIterations();
          }
          return 1;
        };
        var mr = function() {
          if (_ !== void 0) {
            return _;
          }
          if (n !== void 0) {
            return n;
          }
          if (c) {
            return c.getDelay();
          }
          return 0;
        };
        var pr = function() {
          return u;
        };
        var Ar = function(r2) {
          f2 = r2;
          Kr(true);
          return x;
        };
        var gr = function(r2) {
          a = r2;
          Kr(true);
          return x;
        };
        var Cr = function(r2) {
          n = r2;
          Kr(true);
          return x;
        };
        var br = function(r2) {
          i2 = r2;
          Kr(true);
          return x;
        };
        var _r = function(r2) {
          if (!B && r2 === 0) {
            r2 = 1;
          }
          e = r2;
          Kr(true);
          return x;
        };
        var Pr = function(r2) {
          t2 = r2;
          Kr(true);
          return x;
        };
        var Sr = function(r2) {
          c = r2;
          return x;
        };
        var Tr = function(r2) {
          if (r2 != null) {
            if (r2.nodeType === 1) {
              D.push(r2);
            } else if (r2.length >= 0) {
              for (var n2 = 0; n2 < r2.length; n2++) {
                D.push(r2[n2]);
              }
            } else {
              console.error("Invalid addElement value");
            }
          }
          return x;
        };
        var xr = function(r2) {
          if (r2 != null) {
            if (Array.isArray(r2)) {
              for (var n2 = 0, e2 = r2; n2 < e2.length; n2++) {
                var i3 = e2[n2];
                i3.parent(x);
                F.push(i3);
              }
            } else {
              r2.parent(x);
              F.push(r2);
            }
          }
          return x;
        };
        var Er = function(r2) {
          var n2 = u !== r2;
          u = r2;
          if (n2) {
            wr(u);
          }
          return x;
        };
        var wr = function(r2) {
          if (B) {
            G().forEach(function(n2) {
              var e2 = n2.effect;
              if (e2.setKeyframes) {
                e2.setKeyframes(r2);
              } else {
                var i3 = new KeyframeEffect(e2.target, r2, e2.getTiming());
                n2.effect = i3;
              }
            });
          }
        };
        var hr = function() {
          I.forEach(function(r3) {
            return r3();
          });
          K.forEach(function(r3) {
            return r3();
          });
          var r2 = o;
          var n2 = v;
          var e2 = s;
          D.forEach(function(i3) {
            var t3 = i3.classList;
            r2.forEach(function(r3) {
              return t3.add(r3);
            });
            n2.forEach(function(r3) {
              return t3.remove(r3);
            });
            for (var a2 in e2) {
              if (e2.hasOwnProperty(a2)) {
                setStyleProperty(i3, a2, e2[a2]);
              }
            }
          });
        };
        var kr = function() {
          M.forEach(function(r3) {
            return r3();
          });
          j.forEach(function(r3) {
            return r3();
          });
          var r2 = P ? 1 : 0;
          var n2 = l;
          var e2 = y;
          var i3 = m;
          D.forEach(function(r3) {
            var t3 = r3.classList;
            n2.forEach(function(r4) {
              return t3.add(r4);
            });
            e2.forEach(function(r4) {
              return t3.remove(r4);
            });
            for (var a2 in i3) {
              if (i3.hasOwnProperty(a2)) {
                setStyleProperty(r3, a2, i3[a2]);
              }
            }
          });
          b = void 0;
          C = void 0;
          _ = void 0;
          h.forEach(function(n3) {
            return n3.c(r2, x);
          });
          k.forEach(function(n3) {
            return n3.c(r2, x);
          });
          k.length = 0;
          T = true;
          if (P) {
            S = true;
          }
          P = true;
        };
        var Rr = function() {
          if (p === 0) {
            return;
          }
          p--;
          if (p === 0) {
            kr();
            if (c) {
              c.animationFinish();
            }
          }
        };
        var Dr = function() {
          D.forEach(function(r2) {
            var n2 = r2.animate(u, { id: w, delay: mr(), duration: lr(), easing: sr(), iterations: yr(), fill: dr(), direction: cr() });
            n2.pause();
            q.push(n2);
          });
          if (q.length > 0) {
            q[0].onfinish = function() {
              Rr();
            };
          }
        };
        var Fr = function() {
          hr();
          if (u.length > 0) {
            if (B) {
              Dr();
            }
          }
          d = true;
        };
        var Wr = function(r2) {
          r2 = Math.min(Math.max(r2, 0), 0.9999);
          if (B) {
            q.forEach(function(n2) {
              n2.currentTime = n2.effect.getComputedTiming().delay + lr() * r2;
              n2.pause();
            });
          }
        };
        var Ir = function(r2) {
          q.forEach(function(r3) {
            r3.effect.updateTiming({ delay: mr(), duration: lr(), easing: sr(), iterations: yr(), fill: dr(), direction: cr() });
          });
          if (r2 !== void 0) {
            Wr(r2);
          }
        };
        var Kr = function(r2, n2, e2) {
          if (r2 === void 0) {
            r2 = false;
          }
          if (n2 === void 0) {
            n2 = true;
          }
          if (r2) {
            F.forEach(function(i3) {
              i3.update(r2, n2, e2);
            });
          }
          if (B) {
            Ir(e2);
          }
          return x;
        };
        var Mr = function(r2, n2) {
          if (r2 === void 0) {
            r2 = false;
          }
          F.forEach(function(e2) {
            e2.progressStart(r2, n2);
          });
          zr();
          A = r2;
          if (!d) {
            Fr();
          }
          Kr(false, true, n2);
          return x;
        };
        var jr = function(r2) {
          F.forEach(function(n2) {
            n2.progressStep(r2);
          });
          Wr(r2);
          return x;
        };
        var qr = function(r2, n2, e2) {
          A = false;
          F.forEach(function(i3) {
            i3.progressEnd(r2, n2, e2);
          });
          if (e2 !== void 0) {
            b = e2;
          }
          S = false;
          P = true;
          if (r2 === 0) {
            C = cr() === "reverse" ? "normal" : "reverse";
            if (C === "reverse") {
              P = false;
            }
            if (B) {
              Kr();
              Wr(1 - n2);
            } else {
              _ = (1 - n2) * lr() * -1;
              Kr(false, false);
            }
          } else if (r2 === 1) {
            if (B) {
              Kr();
              Wr(n2);
            } else {
              _ = n2 * lr() * -1;
              Kr(false, false);
            }
          }
          if (r2 !== void 0 && !c) {
            Lr();
          }
          return x;
        };
        var zr = function() {
          if (d) {
            if (B) {
              q.forEach(function(r2) {
                r2.pause();
              });
            } else {
              D.forEach(function(r2) {
                setStyleProperty(r2, "animation-play-state", "paused");
              });
            }
            E = true;
          }
        };
        var Br = function() {
          F.forEach(function(r2) {
            r2.pause();
          });
          zr();
          return x;
        };
        var Gr = function() {
          Rr();
        };
        var Hr = function() {
          q.forEach(function(r2) {
            r2.play();
          });
          if (u.length === 0 || D.length === 0) {
            Rr();
          }
        };
        var Jr = function() {
          if (B) {
            Wr(0);
            Ir();
          }
        };
        var Lr = function(r2) {
          return new Promise(function(n2) {
            if (r2 === null || r2 === void 0 ? void 0 : r2.sync) {
              g = true;
              U(function() {
                return g = false;
              }, { oneTimeCallback: true });
            }
            if (!d) {
              Fr();
            }
            if (S) {
              Jr();
              S = false;
            }
            if (T) {
              p = F.length + 1;
              T = false;
            }
            var e2 = function() {
              O(i3, k);
              n2();
            };
            var i3 = function() {
              O(e2, R);
              n2();
            };
            U(i3, { oneTimeCallback: true });
            Q(e2, { oneTimeCallback: true });
            F.forEach(function(r3) {
              r3.play();
            });
            if (B) {
              Hr();
            } else {
              Gr();
            }
            E = false;
          });
        };
        var Nr = function() {
          F.forEach(function(r2) {
            r2.stop();
          });
          if (d) {
            X();
            d = false;
          }
          L();
          R.forEach(function(r2) {
            return r2.c(0, x);
          });
          R.length = 0;
        };
        var Or = function(r2, n2) {
          var e2;
          var i3 = u[0];
          if (i3 !== void 0 && (i3.offset === void 0 || i3.offset === 0)) {
            i3[r2] = n2;
          } else {
            u = __spreadArray([(e2 = { offset: 0 }, e2[r2] = n2, e2)], u, true);
          }
          return x;
        };
        var Qr = function(r2, n2) {
          var e2;
          var i3 = u[u.length - 1];
          if (i3 !== void 0 && (i3.offset === void 0 || i3.offset === 1)) {
            i3[r2] = n2;
          } else {
            u = __spreadArray(__spreadArray([], u, true), [(e2 = { offset: 1 }, e2[r2] = n2, e2)], false);
          }
          return x;
        };
        var Ur = function(r2, n2, e2) {
          return Or(r2, n2).to(r2, e2);
        };
        return x = { parentAnimation: c, elements: D, childAnimations: F, id: w, animationFinish: Rr, from: Or, to: Qr, fromTo: Ur, parent: Sr, play: Lr, pause: Br, stop: Nr, destroy: H2, keyframes: Er, addAnimation: xr, addElement: Tr, update: Kr, fill: gr, direction: Ar, iterations: Pr, duration: _r, easing: br, delay: Cr, getWebAnimations: G, getKeyframes: pr, getFill: dr, getDirection: cr, getDelay: mr, getIterations: yr, getEasing: sr, getDuration: lr, afterAddRead: rr, afterAddWrite: nr, afterClearStyles: vr, afterStyles: or, afterRemoveClass: ur, afterAddClass: fr, beforeAddRead: Z, beforeAddWrite: $, beforeClearStyles: ar, beforeStyles: tr, beforeRemoveClass: ir, beforeAddClass: er, onFinish: U, isRunning: N, progressStart: Mr, progressStep: jr, progressEnd: qr };
      };
    }
  });

  // node_modules/@ionic/core/dist/esm-es5/index-c71c5417.js
  function map(e, t2) {
    if (e.isOk) {
      var r = t2(e.value);
      if (r instanceof Promise) {
        return r.then(function(e2) {
          return ok(e2);
        });
      } else {
        return ok(r);
      }
    }
    if (e.isErr) {
      var n = e.value;
      return err(n);
    }
    throw "should never get here";
  }
  var __defProp, __export, result_exports, ok, err, unwrap, unwrapErr, getMode, CAPTURE_EVENT_SUFFIX, CAPTURE_EVENT_REGEX, hostRefs, getHostRef, consoleError, win2, doc2, H, plt, supportsListenerOptions, promiseResolve, supportsConstructableStylesheets, queuePending, queueDomReads, queueDomWrites, queueTask, consume, flush, nextTick, readTask, writeTask;
  var init_index_c71c5417 = __esm({
    "node_modules/@ionic/core/dist/esm-es5/index-c71c5417.js"() {
      __defProp = Object.defineProperty;
      __export = function(e, t2) {
        for (var r in t2)
          __defProp(e, r, { get: t2[r], enumerable: true });
      };
      result_exports = {};
      __export(result_exports, { err: function() {
        return err;
      }, map: function() {
        return map;
      }, ok: function() {
        return ok;
      }, unwrap: function() {
        return unwrap;
      }, unwrapErr: function() {
        return unwrapErr;
      } });
      ok = function(e) {
        return { isOk: true, isErr: false, value: e };
      };
      err = function(e) {
        return { isOk: false, isErr: true, value: e };
      };
      unwrap = function(e) {
        if (e.isOk) {
          return e.value;
        } else {
          throw e.value;
        }
      };
      unwrapErr = function(e) {
        if (e.isErr) {
          return e.value;
        } else {
          throw e.value;
        }
      };
      getMode = function(e) {
        return getHostRef(e).D;
      };
      CAPTURE_EVENT_SUFFIX = "Capture";
      CAPTURE_EVENT_REGEX = new RegExp(CAPTURE_EVENT_SUFFIX + "$");
      hostRefs = /* @__PURE__ */ new WeakMap();
      getHostRef = function(e) {
        return hostRefs.get(e);
      };
      consoleError = function(e, t2) {
        return (0, console.error)(e, t2);
      };
      win2 = typeof window !== "undefined" ? window : {};
      doc2 = win2.document || { head: {} };
      H = win2.HTMLElement || function() {
        function e() {
        }
        return e;
      }();
      plt = { p: 0, t: "", jmp: function(e) {
        return e();
      }, raf: function(e) {
        return requestAnimationFrame(e);
      }, ael: function(e, t2, r, n) {
        return e.addEventListener(t2, r, n);
      }, rel: function(e, t2, r, n) {
        return e.removeEventListener(t2, r, n);
      }, ce: function(e, t2) {
        return new CustomEvent(e, t2);
      } };
      supportsListenerOptions = function() {
        var e = false;
        try {
          doc2.addEventListener("e", null, Object.defineProperty({}, "passive", { get: function() {
            e = true;
          } }));
        } catch (e2) {
        }
        return e;
      }();
      promiseResolve = function(e) {
        return Promise.resolve(e);
      };
      supportsConstructableStylesheets = function() {
        try {
          new CSSStyleSheet();
          return typeof new CSSStyleSheet().replaceSync === "function";
        } catch (e) {
        }
        return false;
      }();
      queuePending = false;
      queueDomReads = [];
      queueDomWrites = [];
      queueTask = function(e, t2) {
        return function(r) {
          e.push(r);
          if (!queuePending) {
            queuePending = true;
            if (t2 && plt.p & 4) {
              nextTick(flush);
            } else {
              plt.raf(flush);
            }
          }
        };
      };
      consume = function(e) {
        for (var t2 = 0; t2 < e.length; t2++) {
          try {
            e[t2](performance.now());
          } catch (e2) {
            consoleError(e2);
          }
        }
        e.length = 0;
      };
      flush = function() {
        consume(queueDomReads);
        {
          consume(queueDomWrites);
          if (queuePending = queueDomReads.length > 0) {
            plt.raf(flush);
          }
        }
      };
      nextTick = function(e) {
        return promiseResolve().then(e);
      };
      readTask = queueTask(queueDomReads, false);
      writeTask = queueTask(queueDomWrites, true);
    }
  });

  // node_modules/@ionic/core/dist/esm-es5/ionic-global-b9c0d1da.js
  var Config, config, defaultMode, getIonMode;
  var init_ionic_global_b9c0d1da = __esm({
    "node_modules/@ionic/core/dist/esm-es5/ionic-global-b9c0d1da.js"() {
      init_index_c71c5417();
      Config = function() {
        function i2() {
          this.m = /* @__PURE__ */ new Map();
        }
        i2.prototype.reset = function(i3) {
          this.m = new Map(Object.entries(i3));
        };
        i2.prototype.get = function(i3, t2) {
          var n = this.m.get(i3);
          return n !== void 0 ? n : t2;
        };
        i2.prototype.getBoolean = function(i3, t2) {
          if (t2 === void 0) {
            t2 = false;
          }
          var n = this.m.get(i3);
          if (n === void 0) {
            return t2;
          }
          if (typeof n === "string") {
            return n === "true";
          }
          return !!n;
        };
        i2.prototype.getNumber = function(i3, t2) {
          var n = parseFloat(this.m.get(i3));
          return isNaN(n) ? t2 !== void 0 ? t2 : NaN : n;
        };
        i2.prototype.set = function(i3, t2) {
          this.m.set(i3, t2);
        };
        return i2;
      }();
      config = new Config();
      getIonMode = function(i2) {
        return i2 && getMode(i2) || defaultMode;
      };
    }
  });

  // node_modules/@ionic/core/dist/esm-es5/index-9b0d46f4.js
  var printIonWarning;
  var init_index_9b0d46f4 = __esm({
    "node_modules/@ionic/core/dist/esm-es5/index-9b0d46f4.js"() {
      init_tslib_es6();
      printIonWarning = function(r) {
        var n = [];
        for (var o = 1; o < arguments.length; o++) {
          n[o - 1] = arguments[o];
        }
        return console.warn.apply(console, __spreadArray(["[Ionic Warning]: ".concat(r)], n, false));
      };
    }
  });

  // node_modules/@ionic/core/dist/esm-es5/helpers-da915de8.js
  var componentOnReady, raf;
  var init_helpers_da915de8 = __esm({
    "node_modules/@ionic/core/dist/esm-es5/helpers-da915de8.js"() {
      componentOnReady = function(r, a) {
        if (r.componentOnReady) {
          r.componentOnReady().then(function(r2) {
            return a(r2);
          });
        } else {
          raf(function() {
            return a(r);
          });
        }
      };
      raf = function(r) {
        if (typeof __zone_symbol__requestAnimationFrame === "function") {
          return __zone_symbol__requestAnimationFrame(r);
        }
        if (typeof requestAnimationFrame === "function") {
          return requestAnimationFrame(r);
        }
        return setTimeout(r);
      };
    }
  });

  // node_modules/@ionic/core/dist/esm-es5/index-92f14156.js
  var moveFocus, isVisible, createFocusController, LAST_FOCUS, focusController;
  var init_index_92f14156 = __esm({
    "node_modules/@ionic/core/dist/esm-es5/index-92f14156.js"() {
      init_ionic_global_b9c0d1da();
      init_index_c71c5417();
      init_index_9b0d46f4();
      init_helpers_da915de8();
      moveFocus = function(n) {
        n.tabIndex = -1;
        n.focus();
      };
      isVisible = function(n) {
        return n.offsetParent !== null;
      };
      createFocusController = function() {
        var n = function(n2) {
          var e2 = config.get("focusManagerPriority", false);
          if (e2) {
            var r = document.activeElement;
            if (r !== null && (n2 === null || n2 === void 0 ? void 0 : n2.contains(r))) {
              r.setAttribute(LAST_FOCUS, "true");
            }
          }
        };
        var e = function(n2) {
          var e2 = config.get("focusManagerPriority", false);
          if (Array.isArray(e2) && !n2.contains(document.activeElement)) {
            var r = n2.querySelector("[".concat(LAST_FOCUS, "]"));
            if (r && isVisible(r)) {
              moveFocus(r);
              return;
            }
            for (var i2 = 0, t2 = e2; i2 < t2.length; i2++) {
              var a = t2[i2];
              switch (a) {
                case "content":
                  var o = n2.querySelector('main, [role="main"]');
                  if (o && isVisible(o)) {
                    moveFocus(o);
                    return;
                  }
                  break;
                case "heading":
                  var s = n2.querySelector('h1, [role="heading"][aria-level="1"]');
                  if (s && isVisible(s)) {
                    moveFocus(s);
                    return;
                  }
                  break;
                case "banner":
                  var u = n2.querySelector('header, [role="banner"]');
                  if (u && isVisible(u)) {
                    moveFocus(u);
                    return;
                  }
                  break;
                default:
                  printIonWarning("Unrecognized focus manager priority value ".concat(a));
                  break;
              }
            }
            moveFocus(n2);
          }
        };
        return { saveViewFocus: n, setViewFocus: e };
      };
      LAST_FOCUS = "ion-last-focus";
      focusController = createFocusController();
    }
  });

  // node_modules/@ionic/core/dist/esm-es5/ios.transition-2f45f5c1.js
  var init_ios_transition_2f45f5c1 = __esm({
    "node_modules/@ionic/core/dist/esm-es5/ios.transition-2f45f5c1.js"() {
      init_animation_eab5a4ca();
      init_index_92f14156();
      init_index_a5d50daf();
      init_ionic_global_b9c0d1da();
      init_index_c71c5417();
      init_index_9b0d46f4();
      init_helpers_da915de8();
    }
  });

  // node_modules/@ionic/core/dist/esm-es5/md.transition-6fcc955f.js
  var init_md_transition_6fcc955f = __esm({
    "node_modules/@ionic/core/dist/esm-es5/md.transition-6fcc955f.js"() {
      init_animation_eab5a4ca();
      init_index_92f14156();
      init_index_a5d50daf();
      init_ionic_global_b9c0d1da();
      init_index_c71c5417();
      init_index_9b0d46f4();
      init_helpers_da915de8();
    }
  });

  // node_modules/@ionic/core/dist/esm-es5/index.js
  init_animation_eab5a4ca();
  init_index_92f14156();
  init_ios_transition_2f45f5c1();
  init_md_transition_6fcc955f();

  // node_modules/@ionic/core/dist/esm-es5/gesture-controller-314a54f6.js
  var GestureController = function() {
    function t2() {
      this.gestureId = 0;
      this.requestedStart = /* @__PURE__ */ new Map();
      this.disabledGestures = /* @__PURE__ */ new Map();
      this.disabledScroll = /* @__PURE__ */ new Set();
    }
    t2.prototype.createGesture = function(t3) {
      var i2;
      return new GestureDelegate(this, this.newID(), t3.name, (i2 = t3.priority) !== null && i2 !== void 0 ? i2 : 0, !!t3.disableScroll);
    };
    t2.prototype.createBlocker = function(t3) {
      if (t3 === void 0) {
        t3 = {};
      }
      return new BlockerDelegate(this, this.newID(), t3.disable, !!t3.disableScroll);
    };
    t2.prototype.start = function(t3, i2, n) {
      if (!this.canStart(t3)) {
        this.requestedStart.delete(i2);
        return false;
      }
      this.requestedStart.set(i2, n);
      return true;
    };
    t2.prototype.capture = function(t3, i2, n) {
      if (!this.start(t3, i2, n)) {
        return false;
      }
      var e = this.requestedStart;
      var s = -1e4;
      e.forEach(function(t4) {
        s = Math.max(s, t4);
      });
      if (s === n) {
        this.capturedId = i2;
        e.clear();
        var r = new CustomEvent("ionGestureCaptured", { detail: { gestureName: t3 } });
        document.dispatchEvent(r);
        return true;
      }
      e.delete(i2);
      return false;
    };
    t2.prototype.release = function(t3) {
      this.requestedStart.delete(t3);
      if (this.capturedId === t3) {
        this.capturedId = void 0;
      }
    };
    t2.prototype.disableGesture = function(t3, i2) {
      var n = this.disabledGestures.get(t3);
      if (n === void 0) {
        n = /* @__PURE__ */ new Set();
        this.disabledGestures.set(t3, n);
      }
      n.add(i2);
    };
    t2.prototype.enableGesture = function(t3, i2) {
      var n = this.disabledGestures.get(t3);
      if (n !== void 0) {
        n.delete(i2);
      }
    };
    t2.prototype.disableScroll = function(t3) {
      this.disabledScroll.add(t3);
      if (this.disabledScroll.size === 1) {
        document.body.classList.add(BACKDROP_NO_SCROLL);
      }
    };
    t2.prototype.enableScroll = function(t3) {
      this.disabledScroll.delete(t3);
      if (this.disabledScroll.size === 0) {
        document.body.classList.remove(BACKDROP_NO_SCROLL);
      }
    };
    t2.prototype.canStart = function(t3) {
      if (this.capturedId !== void 0) {
        return false;
      }
      if (this.isDisabled(t3)) {
        return false;
      }
      return true;
    };
    t2.prototype.isCaptured = function() {
      return this.capturedId !== void 0;
    };
    t2.prototype.isScrollDisabled = function() {
      return this.disabledScroll.size > 0;
    };
    t2.prototype.isDisabled = function(t3) {
      var i2 = this.disabledGestures.get(t3);
      if (i2 && i2.size > 0) {
        return true;
      }
      return false;
    };
    t2.prototype.newID = function() {
      this.gestureId++;
      return this.gestureId;
    };
    return t2;
  }();
  var GestureDelegate = function() {
    function t2(t3, i2, n, e, s) {
      this.id = i2;
      this.name = n;
      this.disableScroll = s;
      this.priority = e * 1e6 + i2;
      this.ctrl = t3;
    }
    t2.prototype.canStart = function() {
      if (!this.ctrl) {
        return false;
      }
      return this.ctrl.canStart(this.name);
    };
    t2.prototype.start = function() {
      if (!this.ctrl) {
        return false;
      }
      return this.ctrl.start(this.name, this.id, this.priority);
    };
    t2.prototype.capture = function() {
      if (!this.ctrl) {
        return false;
      }
      var t3 = this.ctrl.capture(this.name, this.id, this.priority);
      if (t3 && this.disableScroll) {
        this.ctrl.disableScroll(this.id);
      }
      return t3;
    };
    t2.prototype.release = function() {
      if (this.ctrl) {
        this.ctrl.release(this.id);
        if (this.disableScroll) {
          this.ctrl.enableScroll(this.id);
        }
      }
    };
    t2.prototype.destroy = function() {
      this.release();
      this.ctrl = void 0;
    };
    return t2;
  }();
  var BlockerDelegate = function() {
    function t2(t3, i2, n, e) {
      this.id = i2;
      this.disable = n;
      this.disableScroll = e;
      this.ctrl = t3;
    }
    t2.prototype.block = function() {
      if (!this.ctrl) {
        return;
      }
      if (this.disable) {
        for (var t3 = 0, i2 = this.disable; t3 < i2.length; t3++) {
          var n = i2[t3];
          this.ctrl.disableGesture(n, this.id);
        }
      }
      if (this.disableScroll) {
        this.ctrl.disableScroll(this.id);
      }
    };
    t2.prototype.unblock = function() {
      if (!this.ctrl) {
        return;
      }
      if (this.disable) {
        for (var t3 = 0, i2 = this.disable; t3 < i2.length; t3++) {
          var n = i2[t3];
          this.ctrl.enableGesture(n, this.id);
        }
      }
      if (this.disableScroll) {
        this.ctrl.enableScroll(this.id);
      }
    };
    t2.prototype.destroy = function() {
      this.unblock();
      this.ctrl = void 0;
    };
    return t2;
  }();
  var BACKDROP_NO_SCROLL = "backdrop-no-scroll";
  var GESTURE_CONTROLLER = new GestureController();

  // node_modules/@ionic/core/dist/esm-es5/index.js
  init_ionic_global_b9c0d1da();
  init_helpers_da915de8();

  // node_modules/@ionic/core/dist/esm-es5/config-49c88215.js
  var IonicSafeString = function() {
    function e(e2) {
      this.value = e2;
    }
    return e;
  }();

  // node_modules/@ionic/core/dist/esm-es5/index-c8c3afda.js
  init_tslib_es6();
  init_index_a5d50daf();

  // node_modules/@ionic/core/dist/esm-es5/hardware-back-button-7f93f261.js
  init_index_a5d50daf();
  init_ionic_global_b9c0d1da();
  init_index_c71c5417();
  var MENU_BACK_BUTTON_PRIORITY = 99;

  // node_modules/@ionic/core/dist/esm-es5/index-c8c3afda.js
  init_index_9b0d46f4();
  init_helpers_da915de8();
  init_ionic_global_b9c0d1da();
  init_animation_eab5a4ca();
  var baseAnimation = function(n) {
    return createAnimation().duration(n ? 400 : 300);
  };
  var menuOverlayAnimation = function(n) {
    var r;
    var e;
    var t2 = n.width + 8;
    var i2 = createAnimation();
    var a = createAnimation();
    if (n.isEndSide) {
      r = t2 + "px";
      e = "0px";
    } else {
      r = -t2 + "px";
      e = "0px";
    }
    i2.addElement(n.menuInnerEl).fromTo("transform", "translateX(".concat(r, ")"), "translateX(".concat(e, ")"));
    var o = getIonMode(n);
    var u = o === "ios";
    var s = u ? 0.2 : 0.25;
    a.addElement(n.backdropEl).fromTo("opacity", 0.01, s);
    return baseAnimation(u).addAnimation([i2, a]);
  };
  var menuPushAnimation = function(n) {
    var r;
    var e;
    var t2 = getIonMode(n);
    var i2 = n.width;
    if (n.isEndSide) {
      r = -i2 + "px";
      e = i2 + "px";
    } else {
      r = i2 + "px";
      e = -i2 + "px";
    }
    var a = createAnimation().addElement(n.menuInnerEl).fromTo("transform", "translateX(".concat(e, ")"), "translateX(0px)");
    var o = createAnimation().addElement(n.contentEl).fromTo("transform", "translateX(0px)", "translateX(".concat(r, ")"));
    var u = createAnimation().addElement(n.backdropEl).fromTo("opacity", 0.01, 0.32);
    return baseAnimation(t2 === "ios").addAnimation([a, o, u]);
  };
  var menuRevealAnimation = function(n) {
    var r = getIonMode(n);
    var e = n.width * (n.isEndSide ? -1 : 1) + "px";
    var t2 = createAnimation().addElement(n.contentEl).fromTo("transform", "translateX(0px)", "translateX(".concat(e, ")"));
    return baseAnimation(r === "ios").addAnimation(t2);
  };
  var createMenuController = function() {
    var n = /* @__PURE__ */ new Map();
    var r = [];
    var e = function(n2) {
      return __awaiter(void 0, void 0, void 0, function() {
        var r2;
        return __generator(this, function(e2) {
          switch (e2.label) {
            case 0:
              return [4, c(n2, true)];
            case 1:
              r2 = e2.sent();
              if (r2) {
                return [2, r2.open()];
              }
              return [2, false];
          }
        });
      });
    };
    var t2 = function(n2) {
      return __awaiter(void 0, void 0, void 0, function() {
        var r2;
        return __generator(this, function(e2) {
          switch (e2.label) {
            case 0:
              return [4, n2 !== void 0 ? c(n2, true) : f2()];
            case 1:
              r2 = e2.sent();
              if (r2 !== void 0) {
                return [2, r2.close()];
              }
              return [2, false];
          }
        });
      });
    };
    var i2 = function(n2) {
      return __awaiter(void 0, void 0, void 0, function() {
        var r2;
        return __generator(this, function(e2) {
          switch (e2.label) {
            case 0:
              return [4, c(n2, true)];
            case 1:
              r2 = e2.sent();
              if (r2) {
                return [2, r2.toggle()];
              }
              return [2, false];
          }
        });
      });
    };
    var a = function(n2, r2) {
      return __awaiter(void 0, void 0, void 0, function() {
        var e2;
        return __generator(this, function(t3) {
          switch (t3.label) {
            case 0:
              return [4, c(r2)];
            case 1:
              e2 = t3.sent();
              if (e2) {
                e2.disabled = !n2;
              }
              return [2, e2];
          }
        });
      });
    };
    var o = function(n2, r2) {
      return __awaiter(void 0, void 0, void 0, function() {
        var e2;
        return __generator(this, function(t3) {
          switch (t3.label) {
            case 0:
              return [4, c(r2)];
            case 1:
              e2 = t3.sent();
              if (e2) {
                e2.swipeGesture = n2;
              }
              return [2, e2];
          }
        });
      });
    };
    var u = function(n2) {
      return __awaiter(void 0, void 0, void 0, function() {
        var r2, r2;
        return __generator(this, function(e2) {
          switch (e2.label) {
            case 0:
              if (!(n2 != null))
                return [3, 2];
              return [4, c(n2)];
            case 1:
              r2 = e2.sent();
              return [2, r2 !== void 0 && r2.isOpen()];
            case 2:
              return [4, f2()];
            case 3:
              r2 = e2.sent();
              return [2, r2 !== void 0];
          }
        });
      });
    };
    var s = function(n2) {
      return __awaiter(void 0, void 0, void 0, function() {
        var r2;
        return __generator(this, function(e2) {
          switch (e2.label) {
            case 0:
              return [4, c(n2)];
            case 1:
              r2 = e2.sent();
              if (r2) {
                return [2, !r2.disabled];
              }
              return [2, false];
          }
        });
      });
    };
    var c = function(n2) {
      var e2 = [];
      for (var t3 = 1; t3 < arguments.length; t3++) {
        e2[t3 - 1] = arguments[t3];
      }
      return __awaiter(void 0, __spreadArray([n2], e2, true), void 0, function(n3, e3) {
        var t4, i3, a2;
        if (e3 === void 0) {
          e3 = false;
        }
        return __generator(this, function(o2) {
          switch (o2.label) {
            case 0:
              return [4, x()];
            case 1:
              o2.sent();
              if (n3 === "start" || n3 === "end") {
                t4 = r.filter(function(r2) {
                  return r2.side === n3 && !r2.disabled;
                });
                if (t4.length >= 1) {
                  if (t4.length > 1 && e3) {
                    printIonWarning('menuController queried for a menu on the "'.concat(n3, '" side, but ').concat(t4.length, " menus were found. The first menu reference will be used. If this is not the behavior you want then pass the ID of the menu instead of its side."), t4.map(function(n4) {
                      return n4.el;
                    }));
                  }
                  return [2, t4[0].el];
                }
                i3 = r.filter(function(r2) {
                  return r2.side === n3;
                });
                if (i3.length >= 1) {
                  if (i3.length > 1 && e3) {
                    printIonWarning('menuController queried for a menu on the "'.concat(n3, '" side, but ').concat(i3.length, " menus were found. The first menu reference will be used. If this is not the behavior you want then pass the ID of the menu instead of its side."), i3.map(function(n4) {
                      return n4.el;
                    }));
                  }
                  return [2, i3[0].el];
                }
              } else if (n3 != null) {
                return [2, b(function(r2) {
                  return r2.menuId === n3;
                })];
              }
              a2 = b(function(n4) {
                return !n4.disabled;
              });
              if (a2) {
                return [2, a2];
              }
              return [2, r.length > 0 ? r[0].el : void 0];
          }
        });
      });
    };
    var f2 = function() {
      return __awaiter(void 0, void 0, void 0, function() {
        return __generator(this, function(n2) {
          switch (n2.label) {
            case 0:
              return [4, x()];
            case 1:
              n2.sent();
              return [2, w()];
          }
        });
      });
    };
    var v = function() {
      return __awaiter(void 0, void 0, void 0, function() {
        return __generator(this, function(n2) {
          switch (n2.label) {
            case 0:
              return [4, x()];
            case 1:
              n2.sent();
              return [2, g()];
          }
        });
      });
    };
    var d = function() {
      return __awaiter(void 0, void 0, void 0, function() {
        return __generator(this, function(n2) {
          switch (n2.label) {
            case 0:
              return [4, x()];
            case 1:
              n2.sent();
              return [2, A()];
          }
        });
      });
    };
    var _ = function(r2, e2) {
      n.set(r2, e2);
    };
    var m = function(n2) {
      if (r.indexOf(n2) < 0) {
        r.push(n2);
      }
    };
    var l = function(n2) {
      var e2 = r.indexOf(n2);
      if (e2 > -1) {
        r.splice(e2, 1);
      }
    };
    var h = function(n2, r2, e2) {
      return __awaiter(void 0, void 0, void 0, function() {
        var t3;
        return __generator(this, function(i3) {
          switch (i3.label) {
            case 0:
              if (A()) {
                return [2, false];
              }
              if (!r2)
                return [3, 3];
              return [4, f2()];
            case 1:
              t3 = i3.sent();
              if (!(t3 && n2.el !== t3))
                return [3, 3];
              return [4, t3.setOpen(false, false)];
            case 2:
              i3.sent();
              i3.label = 3;
            case 3:
              return [2, n2._setOpen(r2, e2)];
          }
        });
      });
    };
    var p = function(r2, e2) {
      var t3 = n.get(r2);
      if (!t3) {
        throw new Error("animation not registered");
      }
      var i3 = t3(e2);
      return i3;
    };
    var w = function() {
      return b(function(n2) {
        return n2._isOpen;
      });
    };
    var g = function() {
      return r.map(function(n2) {
        return n2.el;
      });
    };
    var A = function() {
      return r.some(function(n2) {
        return n2.isAnimating;
      });
    };
    var b = function(n2) {
      var e2 = r.find(n2);
      if (e2 !== void 0) {
        return e2.el;
      }
      return void 0;
    };
    var x = function() {
      return Promise.all(Array.from(document.querySelectorAll("ion-menu")).map(function(n2) {
        return new Promise(function(r2) {
          return componentOnReady(n2, r2);
        });
      }));
    };
    _("reveal", menuRevealAnimation);
    _("push", menuPushAnimation);
    _("overlay", menuOverlayAnimation);
    doc === null || doc === void 0 ? void 0 : doc.addEventListener("ionBackButton", function(n2) {
      var r2 = w();
      if (r2) {
        n2.detail.register(MENU_BACK_BUTTON_PRIORITY, function() {
          return r2.close();
        });
      }
    });
    return { registerAnimation: _, get: c, getMenus: v, getOpen: f2, isEnabled: s, swipeGesture: o, isAnimating: d, isOpen: u, enable: a, toggle: i2, close: t2, open: e, _getOpenSync: w, _createAnimation: p, _register: m, _unregister: l, _setOpen: h };
  };
  var menuController = createMenuController();

  // node_modules/@ionic/core/dist/esm-es5/overlays-0d212972.js
  init_tslib_es6();
  init_index_a5d50daf();
  init_helpers_da915de8();
  init_ionic_global_b9c0d1da();

  // node_modules/@ionic/core/dist/esm-es5/framework-delegate-63d1a679.js
  init_helpers_da915de8();

  // node_modules/@ionic/core/dist/esm-es5/overlays-0d212972.js
  init_index_9b0d46f4();
  var createController = function(e) {
    return { create: function(n) {
      return createOverlay(e, n);
    }, dismiss: function(n, r, t2) {
      return dismissOverlay(document, n, r, e, t2);
    }, getTop: function() {
      return __awaiter(this, void 0, void 0, function() {
        return __generator(this, function(n) {
          return [2, getPresentedOverlay(document, e)];
        });
      });
    } };
  };
  var alertController = createController("ion-alert");
  var actionSheetController = createController("ion-action-sheet");
  var loadingController = createController("ion-loading");
  var modalController = createController("ion-modal");
  var pickerController = createController("ion-picker-legacy");
  var popoverController = createController("ion-popover");
  var toastController = createController("ion-toast");
  var createOverlay = function(e, n) {
    if (typeof window !== "undefined" && typeof window.customElements !== "undefined") {
      return window.customElements.whenDefined(e).then(function() {
        var r = document.createElement(e);
        r.classList.add("overlay-hidden");
        Object.assign(r, Object.assign(Object.assign({}, n), { hasController: true }));
        getAppRoot(document).appendChild(r);
        return new Promise(function(e2) {
          return componentOnReady(r, e2);
        });
      });
    }
    return Promise.resolve();
  };
  var isOverlayHidden = function(e) {
    return e.classList.contains("overlay-hidden");
  };
  var dismissOverlay = function(e, n, r, t2, o) {
    var a = getPresentedOverlay(e, t2, o);
    if (!a) {
      return Promise.reject("overlay does not exist");
    }
    return a.dismiss(n, r);
  };
  var getOverlays = function(e, n) {
    if (n === void 0) {
      n = "ion-alert,ion-action-sheet,ion-loading,ion-modal,ion-picker-legacy,ion-popover,ion-toast";
    }
    return Array.from(e.querySelectorAll(n)).filter(function(e2) {
      return e2.overlayIndex > 0;
    });
  };
  var getPresentedOverlays = function(e, n) {
    return getOverlays(e, n).filter(function(e2) {
      return !isOverlayHidden(e2);
    });
  };
  var getPresentedOverlay = function(e, n, r) {
    var t2 = getPresentedOverlays(e, n);
    return r === void 0 ? t2[t2.length - 1] : t2.find(function(e2) {
      return e2.id === r;
    });
  };
  var getAppRoot = function(e) {
    return e.querySelector("ion-app") || e.body;
  };

  // node_modules/@ionic/core/dist/esm-es5/index.js
  init_index_a5d50daf();
  init_index_c71c5417();
  init_index_9b0d46f4();

  // js/url.js
  var root_path = document.querySelector("#root_path").content;
  var root_url = root_path;
  var etc_url = root_url + "/etc";
  var ui_url = root_url + "/ui";
  var ui_auth_url = ui_url + "/auth";

  // js/fetch.js
  async function fetch_data(url) {
    return await fetch(url, { credentials: "include" }).then((response) => {
      if (!response.ok) {
        throw new Error("Unauthorized API endpoint:" + response.url);
      }
      return response.json();
    }).catch((err2) => {
      return false;
    });
  }
  async function fetch_html(selector, url) {
    return await fetch(url, { credentials: "include" }).then((response) => {
      if (!response.ok) {
        throw new Error("Unauthorized API endpoint:" + response.url);
      }
      return response.text();
    }).then((html) => {
      parent = document.querySelector(selector);
      if (parent.firstElementChild) {
        parent.firstElementChild.remove();
      }
      parent.insertAdjacentHTML("beforeend", html);
      return true;
    }).catch((err2) => {
      return false;
    });
  }

  // js/etc.js
  var etc_form = document.querySelector("#etc-form");
  etc_form.addEventListener("submit", async function(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(this)), instrument2 = get_instrument(), results = fetch_data(etc_url + "/" + instrument2 + "/data?" + new URLSearchParams(data));
    fetch_html(
      "#modal-slot",
      ui_url + "/etc_results?" + new URLSearchParams(await results)
    );
  });
  function update_filters(instrument2) {
    if (select_filters = document.querySelector("#select-filters")) {
      while (select_filters.firstChild) {
        select_filters.lastChild.remove();
      }
      instrumentID = instrument2.id;
      filters = instrument2.filters;
      let f_default = get_filterID(instrumentID);
      for (f in filters) {
        let option = document.createElement("ion-select-option");
        option.value = f;
        filter = filters[f];
        option.innerHTML = filter.name;
        select_filters.appendChild(option);
        if (!f_default && (filter.default || !f_default)) {
          f_default = f;
        }
      }
      select_filters.value = f_default;
      update_filter(instrumentID, f_default);
      select_filters.addEventListener("ionChange", (event) => {
        update_filter(instrumentID, event.detail.value);
      });
    }
  }

  // js/instrument.js
  var instruments_cache = null;
  async function get_instruments() {
    if (!instruments_cache) {
      const loading = await loadingController.create({
        message: "Loading instruments ...",
        duration: 1e4
      });
      loading.present();
      instruments_cache = fetch_data(etc_url + "/instruments");
      loading.dismiss();
    }
    return instruments_cache;
  }
  function get_instrumentID() {
    return localStorage.getItem("pyDIETDefaultInstrument");
  }
  function update_instrument(instrumentID2) {
    get_instruments().then((instruments) => {
      instrument = instruments[instrumentID2];
      update_filters(instrument);
      localStorage.setItem("pyDIETDefaultInstrument", instrumentID2);
      return instrumentID2;
    });
  }
  function get_filterID(instrumentID2) {
    return localStorage.getItem("pyDIETDefaultFilter_" + instrumentID2);
  }
  function update_filter(instrumentID2, filterID) {
    if (filterID) {
      localStorage.setItem("pyDIETDefaultFilter_" + instrumentID2, filterID);
      return filterID;
    } else {
      return get_filterID(instrumentID2);
    }
  }

  // js/theme.js
  var themes = ["Light", "Dark", "Auto"];
  var theme_icons = ["sunny", "moon", "contrast"];
  var prefersdark = window.matchMedia("(prefers-color-scheme: dark)");
  function toggle_dark_theme(isdark) {
    document.body.classList.toggle("dark", isdark);
  }
  function get_theme() {
    return localStorage.getItem("pyDIETDefaultTheme");
  }
  function update_theme(theme2) {
    if (theme2) {
      localStorage.setItem("pyDIETDefaultTheme", theme2);
    } else {
      theme2 = get_theme();
    }
    toggle_dark_theme(
      typeof theme2 === "string" && theme2.includes("dark") || !(typeof theme2 === "string" && theme2.includes("light")) && prefersdark.matches
    );
  }

  // js/settings.js
  function setup_theme_settings() {
    if (theme_segment = document.querySelector("#theme-segment")) {
      for (t in themes) {
        let button = document.createElement("ion-segment-button"), icon = document.createElement("ion-icon"), label = document.createElement("ion-label");
        button.value = themes[t].toLowerCase();
        label.innerHTML = themes[t];
        button.appendChild(label);
        icon.name = theme_icons[t];
        button.appendChild(icon);
        theme_segment.appendChild(button);
      }
      theme_segment.value = theme = get_theme();
      update_theme(theme);
      theme_segment.addEventListener("ionChange", (event) => {
        update_theme(event.detail.value);
      });
    }
  }
  function setup_instrument_settings(instruments) {
    if (instrument_segment = document.querySelector("#instrument-segment")) {
      let i_default = get_instrumentID();
      for (i in instruments) {
        let button = document.createElement("ion-segment-button"), icon = document.createElement("ion-icon"), label = document.createElement("ion-label");
        button.value = i;
        instrument = instruments[i];
        label.innerHTML = instrument.name;
        button.appendChild(label);
        icon.name = "videocam";
        button.appendChild(icon);
        instrument_segment.appendChild(button);
        if (!i_default && (instrument.default || !i_default)) {
          i_default = i;
        }
      }
      instrument_segment.value = i_default;
      update_instrument(i_default);
      instrument_segment.addEventListener("ionChange", (event) => {
        update_instrument(event.detail.value);
      });
    }
  }

  // js/main.js
  setup_theme_settings();
  get_instruments().then((instruments) => {
    setup_instrument_settings(instruments);
  });
})();
/*!
 * (C) Ionic http://ionicframework.com - MIT License
 */
