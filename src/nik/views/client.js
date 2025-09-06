(() => {
  class Observable {
    constructor(value) {
      this._value = value;
      this._global_listeners = [];
      this._listeners = {};
      this.is_primitive = isPrimitive(value);
      this.is_dict = isDict(value);
      this.is_array = Array.isArray(value);
    }

    get value() {
      return this._value;
    }

    getPropValue(prop) {
      if (!this.is_dict) {
        console.warn("Observable is not a dictionary");
        return undefined;
      }
      return this._value[prop];
    }

    update(newValue, path, operation) {
      const oldValue = this._value;

      // full update
      if (!path) {
        if (operation === "append") {
          if (!this.is_array) {
            return console.error(
              "Append operation is only supported for arrays",
              { currentValue: oldValue, newValue }
            );
          }

          this._value = [...oldValue, newValue];
          this._global_listeners.forEach((fn) =>
            fn(oldValue, this._value, path, operation)
          );
        } else if (!deepEqual(this._value, newValue)) {
          const field_listeners = [];
          if (this.is_dict) {
            for (const [key, listeners] of Object.entries(this._listeners)) {
              if (
                // Key added or its value changed
                !deepEqual(this._value[key], newValue[key]) ||
                // Key removed
                (!newValue[key] && this._value[key] !== undefined)
              ) {
                field_listeners.push(
                  ...listeners.map((fn) => {
                    return () => fn(oldValue[key], newValue[key], key);
                  })
                );
              }
            }
          }

          this._value = newValue;
          this._global_listeners.forEach((fn) =>
            fn(oldValue, newValue, path, operation)
          );
          field_listeners.forEach((fn) => fn());
        }
      } else {
        if (this.is_primitive) {
          return console.error(
            "Primitive values cannot be updated via path parameter",
            { currentValue: this._value, newValue, path }
          );
        } else if (this.is_dict) {
          if (!deepEqual(this._value[path], newValue)) {
            this._value[path] = newValue;
            const listeners = this._listeners[path] || [];
            listeners.forEach((fn) => fn(newValue));
          }
        } else if (this.is_array) {
          console.error("not implemented for arrays", {
            currentValue: this._value,
            newValue,
            path,
          });
        } else {
          throw new Error(
            `Unsupported type for path update: ${typeof this._value}`
          );
        }
      }
    }

    subscribe(fn, path) {
      if (!path) {
        this._global_listeners.push(fn);
      } else {
        if (!this._listeners[path]) {
          this._listeners[path] = [];
        }
        this._listeners[path].push(fn);
      }
    }

    bool() {
      if (this.is_primitive) {
        return Boolean(this._value);
      } else if (this.is_dict) {
        return Object.keys(this._value).length > 0;
      } else if (this.is_array) {
        return this._value.length > 0;
      }
      return false;
    }

    equal_to(value, path) {
      let valueToCompare = this._value;

      if (path) {
        if (!this.is_dict) {
          return console.warn(
            'Argument "path" given for a non-dictionary observable',
            { path, value, observable: this }
          );
        }
        valueToCompare = this._value[path];
      }

      // treat null and undefined as equal
      if (value === null && valueToCompare === undefined) {
        return true;
      }

      return deepEqual(valueToCompare, value);
    }

    not_equal_to(value, path) {
      return !this.equal_to(value, path);
    }
  }

  function isPrimitive(value) {
    return (
      value === null ||
      typeof value === "boolean" ||
      typeof value === "number" ||
      typeof value === "string"
    );
  }

  function isDict(obj) {
    return (
      obj !== null &&
      typeof obj === "object" &&
      !Array.isArray(obj) &&
      Object.prototype.toString.call(obj) === "[object Object]" &&
      Object.getPrototypeOf(obj) === Object.prototype
    );
  }

  /**
   * Compares two values for deep equality.
   * Supports primitive values, arrays, and plain objects.
   *
   * @param {any} a - First value to compare.
   * @param {any} b - Second value to compare.
   * @returns {boolean} - True if values are deeply equal, false otherwise.
   */
  function deepEqual(a, b) {
    if (a === b) {
      return true;
    }

    if (typeof a !== typeof b || a === null || b === null) {
      return false;
    }

    if (Array.isArray(a) && Array.isArray(b)) {
      if (a.length !== b.length) {
        return false;
      }
      for (let i = 0; i < a.length; i++) {
        if (!deepEqual(a[i], b[i])) {
          return false;
        }
      }
      return true;
    }

    if (isDict(a) && isDict(b)) {
      const keysA = Object.keys(a);
      const keysB = Object.keys(b);
      if (keysA.length !== keysB.length) {
        return false;
      }
      for (const key of keysA) {
        if (!deepEqual(a[key], b[key])) {
          return false;
        }
      }
      return true;
    }

    return false;
  }

  function debounce(func, wait) {
    let timeout;
    return function (...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  }

  /**
   * nik version of fetch that includes additional headers
   *
   * @param {String} url
   * @param {Object} options
   * @param {Object} options.type - The type of request (e.g., "link", "partial")
   * @param {String} options.previousPath - The previous path for the request
   * @param {Object} fetchOptions.headers - Additional headers to include in the request
   * @param {String} fetchOptions.method - The HTTP method to use (default: "get")
   * @param {String} fetchOptions.body - The body of the request (eg: for POST requests)
   * @returns {Promise<Response>} The fetch response
   */
  function nikFetch(
    url,
    { type = "link", previousPath } = {},
    { method = "get", body, headers = {} } = {}
  ) {
    let contentType = "";
    if (type === "link" || type === "partial") {
      contentType = "application/json";
    } else if (type === "form" && !headers["content-type"]) {
      throw new Error("Content-Type must be set for form requests.");
    }

    return fetch(url, {
      method,
      headers: {
        "x-nik-request": "1",
        "x-nik-request-type": type,
        ...(previousPath && { "x-nik-previous-path": previousPath }),
        "content-type": contentType,
        ...headers,
      },
      ...(body && { body }),
    });
  }

  /**
   * @param {String} callbackName
   * @returns {Function}
   * @throws {Error} If the callback does not exist
   * */
  function getCallback(callbackName) {
    const callback = callbacks[callbackName];
    if (!callback) {
      throw new Error(`Callback "${callbackName}" does not exist.`);
    }
    return (...args) => {
      return callback(...args);
    };
  }

  /**
   * @param {String} id
   * @returns {HTMLElement}
   * @throws {Error} If the element with the given ID does not exist
   */
  function getElementById(id) {
    const elm = document.getElementById(id);
    if (!elm) {
      throw new Error(`Element with ID "${id}" does not exist.`);
    }
    return elm;
  }

  const callbacks = {
    consoleLog: (message) => {
      console.log("ConsoleLog:", message);
    },

    toggleShow(elementId, { observable } = {}) {
      const element = getElementById(elementId);
      if (observable.bool()) {
        element.style.display = "block";
      } else {
        element.style.display = "none";
      }
    },

    /**
     * Toggles a class on an element based on the value of an observable.
     * The condition result should be true to add the class, false to remove it.
     *
     * @param {String} elementId ID of the element to toggle class on
     * @param {equal_to|not_equal_to} op operation to perform
     * @param {Any} op_value value to compare against
     * @param {String} className class to toggle
     * @returns {void}
     */
    toggleClass: (
      elementId,
      op,
      op_value,
      className,
      { observable, observableProp } = {}
    ) => {
      const element = getElementById(elementId);

      let result = observable[op](op_value, observableProp);
      if (result) {
        element.classList.add(className);
      } else {
        element.classList.remove(className);
      }
    },

    reactiveAttribute: (elmId, attribute, condition, { observable } = {}) => {
      const elm = getElementById(elmId);

      if (BOOLEAN_ATTRIBUTES.includes(attribute)) {
        const _value =
          condition === "WhenNot" ? !observable.value : observable.value;
        if (_value) {
          elm.setAttribute(attribute, "");
        } else {
          elm.removeAttribute(attribute);
        }
      } else {
        throw new Error("Not implemented for attribute: " + attribute);
      }
    },

    updateFormStateClass: (formId, loadingClass, errorClass, { app } = {}) => {
      const formState = app.getObservable(formId + "_form_state");
      const form = getElementById(formId);

      if (formState.value === "loading") {
        form.classList.add(loadingClass);
        form.classList.remove(errorClass);
      } else if (formState.value === "error") {
        form.classList.add(errorClass);
        form.classList.remove(loadingClass);
      } else if (formState.value === "ready") {
        form.classList.remove(loadingClass);
        form.classList.remove(errorClass);
      }
    },

    /**
     *
     * @param {String} template Html template
     * @param {String} parentId Element id of the parent container
     * @param {Object} options
     * @param {Observable} options.observable Observable that contains the data to render
     * @param {String} options.observableProp Property of the observable to iterate over
     * @param {String} options.operation Operation to perform (e.g., "append")
     * @param {any} options.oldValue Old value of the observable
     * @param {any} options.newValue New value of the observable
     * @param {NikApp} options.app Instance of the NikApp
     * @returns {void}
     */
    insertElements: (
      template,
      parentId,
      { observable, observableProp, operation, oldValue, newValue, app } = {}
    ) => {
      const parent = getElementById(parentId);

      let iterableValue = observable.value;
      if (operation === "append") {
        iterableValue = newValue.slice(oldValue.length);
      } else if (observableProp) {
        iterableValue = observable.getPropValue(observableProp);
      }

      if (!iterableValue) {
        parent.innerHTML = "";
        return;
      }

      if (!Array.isArray(iterableValue)) {
        console.warn("InsertElements callback requires an array observable.", {
          observable,
          observableProp,
          iterableValue,
        });
        return;
      }

      function resolvePath(obj, path) {
        return path.split(".").reduce((acc, part) => acc && acc[part], obj);
      }

      let html = "";
      for (const value of iterableValue) {
        html += template.replace(/{{\s*([^}]+)\s*}}/g, (_, expr) => {
          if (expr.startsWith("value.")) {
            return resolvePath({ value }, expr);
          }
          return resolvePath(value, expr);
        });
      }

      if (operation === "append") {
        parent.innerHTML += html;
      } else {
        parent.innerHTML = html;
      }
    },

    /**
     * Triggers a partial fetch source.
     *
     * @param {Object} data Query parameters to send with the request
     * @param {String} path The base path for the fetch request
     * @param {Object} options
     * @param {NikApp} options.app Instance of the NikApp
     * @returns {void}
     */
    partialFetch: (data, path, { app } = {}) => {
      const basePath = path || "";

      const params = new URLSearchParams();
      for (const key in data) {
        if (data.hasOwnProperty(key)) {
          params.append(key, data[key]);
        }
      }
      const queryString = params.toString();

      let fetchUrl = basePath;
      if (queryString) {
        fetchUrl += (basePath.includes("?") ? "&" : "?") + queryString;
      }

      app.loadAndReplace(fetchUrl, false, true);
    },

    updateState: (observableKey, observableProp, value, operation, { app }) => {
      let observable = app.getObservable(observableKey);
      observable.update(value, observableProp, operation);
    },
  };

  const BOOLEAN_ATTRIBUTES = [
    "disabled",
    "hidden",
    "checked",
    "readonly",
    "required",
  ];

  class NikApp {
    page = {
      loading: new Observable(false),
      error: new Observable(false),
      observables: {},
      onClickSubscriptions: {},
      onChangeSubscriptions: {},
      onSubmitSubscriptions: {},
    };

    previousPath = null;
    currentPath = window.location.pathname;

    actions = {
      registerObservable: (name, initialValue) => {
        this.page.observables[name] = new Observable(initialValue);
      },

      subscribeObservable: (
        observableKey,
        observableProp,
        callbackName,
        ...callbackArgs
      ) => {
        let observable = this.getObservable(observableKey);
        const callback = getCallback(callbackName);

        observable.subscribe((oldValue, newValue, prop, operation) => {
          return callback(...callbackArgs, {
            observable,
            observableProp,
            operation,
            oldValue,
            newValue,
            app: this,
          });
        }, observableProp);
      },

      onClick: (elmId, callbackName, ...callbackArgs) => {
        if (!this.page.onClickSubscriptions[elmId]) {
          this.page.onClickSubscriptions[elmId] = [];
        }

        this.page.onClickSubscriptions[elmId].push(async (elm_id) => {
          const callback = getCallback(callbackName);
          callback(...callbackArgs, { app: this });
        });
      },

      listenSubmit: (formId, resetAfterSuccess) => {
        this.page.onSubmitSubscriptions[formId] = async (event) => {
          event.preventDefault();

          const formState = this.getObservable(formId + "_form_state", null);
          const updateFormState = (value) => {
            if (formState) {
              formState.update(value);
            }
          };
          const form = event.target;
          const method = form.method ? form.method.toUpperCase() : "GET";
          const action = form.action || window.location.href;
          const formData = new FormData(form);

          let fetchUrl = action;
          let fetchOptions = {
            method,
          };

          const hasFiles = Array.from(formData.values()).some(
            (value) => value instanceof File && value.size > 0
          );

          if (method === "GET") {
            const params = new URLSearchParams(formData).toString();
            fetchUrl += (fetchUrl.includes("?") ? "&" : "?") + params;
          } else if (hasFiles) {
            const payload = {};
            const filePromises = [];

            const readFileAsBase64 = (file) => {
              return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = () => resolve(reader.result);
                reader.onerror = (error) => reject(error);
                reader.readAsDataURL(file);
              });
            };

            for (const key of new Set(formData.keys())) {
              const values = formData.getAll(key);
              const files = values.filter(
                (v) => v instanceof File && v.size > 0
              );

              if (files.length > 0) {
                const fileProcessingPromise = Promise.all(
                  files.map((file) =>
                    readFileAsBase64(file).then((base64) => ({
                      name: file.name,
                      type: file.type,
                      content: base64,
                    }))
                  )
                ).then((processedFiles) => {
                  payload[key] =
                    processedFiles.length > 1
                      ? processedFiles
                      : processedFiles[0];
                });
                filePromises.push(fileProcessingPromise);
              } else {
                payload[key] = values.length > 1 ? values : values[0];
              }
            }

            await Promise.all(filePromises);

            fetchOptions.body = JSON.stringify(payload);
            fetchOptions.headers = {
              "content-type": "application/json",
            };
          } else {
            const filteredFormData = new FormData();
            for (const [key, value] of formData.entries()) {
              if (!(value instanceof File && value.size === 0)) {
                filteredFormData.append(key, value);
              }
            }
            const urlEncoded = new URLSearchParams(filteredFormData).toString();
            fetchOptions.body = urlEncoded;
            fetchOptions.headers = {
              "content-type": "application/x-www-form-urlencoded",
            };
          }

          updateFormState("loading");
          this.page.loading.update(true);
          this.page.error.update(false);

          try {
            const resp = await nikFetch(
              fetchUrl,
              { type: "form" },
              fetchOptions
            );
            const json = await resp.json();

            if (resp.status >= 300) {
              updateFormState("error");
              this.page.error.update(true);
            } else {
              updateFormState("ready");
              this.page.error.update(false);
              if (resetAfterSuccess) {
                form.reset();
              }
            }

            if (json && json.actions) {
              this.run(json.actions);
            }
            this.page.loading.update(false);
          } catch (error) {
            console.error("Fetch error:", error);
            updateFormState("error");
            this.page.loading.update(false);
            this.page.error.update(true);
          }
        };
      },

      updateState: (observableKey, observableProp, value, operation) => {
        let observable = this.getObservable(observableKey);
        observable.update(value, observableProp, operation);
      },

      // TODO: support observableProp
      bindValue: (elmId, observableKey) => {
        const observable = this.getObservable(observableKey);
        const elm = getElementById(elmId);
        let isUpdating = false;

        observable.subscribe((value) => {
          if (isUpdating) {
            return;
          }
          if (elm.type === "checkbox" || elm.type === "radio") {
            elm.checked = value;
          } else {
            elm.value = value;
          }
        });

        if (!this.page.onChangeSubscriptions[elmId]) {
          this.page.onChangeSubscriptions[elmId] = [];
        }
        this.page.onChangeSubscriptions[elmId].push((value) => {
          if (observable.value !== value) {
            isUpdating = true;
            observable.update(value);
            isUpdating = false;
          }
        });
      },

      redirect: (url, full = true) => {
        debounce(() => {
          if (full) {
            window.location.href = url;
          } else {
            this.loadAndReplace(url, true, false);
          }
        }, 100)();
      },

      refreshView: (partial) => {
        this.loadAndReplace(this.currentPath, false, partial);
      },
    };

    run(actions) {
      for (const viewActions of Object.values(actions)) {
        if (Array.isArray(viewActions)) {
          for (const [actionName, ...actionGroups] of viewActions) {
            const method = this.actions[actionName];
            if (method) {
              actionGroups.forEach((params) => {
                try {
                  method.apply(this, params);
                } catch (error) {
                  console.error(
                    `Error executing action "${actionName}" with params:`,
                    params,
                    error
                  );
                }
              });
            } else {
              console.warn(
                `Method "${actionName}" not found in NikApp actions.`
              );
            }
          }
        }
      }
    }

    /**
     * @param {String} observableKey
     * @param {any} defaultVal Value to return if the observable does not exist. If not given an error will be thrown.
     * @returns {Observable|null}
     * @throws {Error} If the observable does not exist and no default value is provided
     */
    getObservable = (observableKey, defaultVal) => {
      const observable = this.page.observables[observableKey];
      if (observable === undefined) {
        if (defaultVal !== undefined) {
          return defaultVal;
        }
        throw new Error(
          `Observable with key "${observableKey}" does not exist.`
        );
      }
      return observable;
    };

    listenChange(elmId, observableKey, valueProp) {
      if (!this.page.onChangeSubscriptions[elmId]) {
        this.page.onChangeSubscriptions[elmId] = [];
      }
      this.page.onChangeSubscriptions[elmId].push((value) => {
        this.page.observables[observableKey].value = value;
      });
    }

    triggerOnClick = (id) => {
      const subscriptions = this.page.onClickSubscriptions[id];
      if (!subscriptions) {
        throw new Error(`No onClick subscriptions found for ID: ${id}`);
      }

      Promise.all(subscriptions.map((callback) => callback(id)));
    };

    loadAndReplace = (urlOrPath, pushState, isPartial) => {
      let requestedPath = urlOrPath;
      if (urlOrPath.startsWith("http")) {
        const urlObj = new URL(urlOrPath);
        requestedPath = urlObj.pathname + urlObj.search + urlObj.hash;
      }

      return nikFetch(
        requestedPath,
        {
          type: isPartial ? "partial" : "link",
          previousPath: this.currentPath,
        },
        {}
      )
        .then(async (response) => {
          const json = await response.json();

          if (!response.ok) {
            console.error("Error fetching url:", {
              url: requestedPath,
              status: response.status,
              statusText: response.statusText,
              body: json,
            });
            return;
          }

          const replaces = getElementById(json.replaces);
          replaces.outerHTML = json.view;

          this.previousPath = this.currentPath;
          if (!isPartial) {
            const newPath = urlOrPath.startsWith("http")
              ? new URL(urlOrPath).pathname
              : urlOrPath;

            this.currentPath = newPath;

            const navState = this.getObservable("page_nav_state", null);
            if (navState) {
              navState.update(newPath);
            }
          }

          if (json.actions) {
            this.run(json.actions);
          }

          if (pushState) {
            window.history.pushState({}, "", urlOrPath);
          }
        })
        .catch((error) => {
          console.error("Fetch error:", error);
        });
    };

    handleClick = (e) => {
      const anchor = e.target.closest("a");
      if (
        anchor &&
        anchor.href &&
        anchor.href.startsWith(window.location.origin) &&
        !anchor.attributes.href.value.startsWith("#") &&
        anchor.dataset.controlled !== "0"
      ) {
        e.preventDefault();
        this.loadAndReplace(anchor.href, true, false);
      } else {
        const { id } = e.target;
        if (id && this.page.onClickSubscriptions[id]) {
          e.preventDefault();
          this.triggerOnClick(id);
        }
      }
    };

    handlePopState = (event) => {
      this.loadAndReplace(window.location.href, false, false);
    };

    handleOnChange = (event) => {
      if (event.target.tagName === "INPUT") {
        let value;
        const id = event.target.id;

        if (event.target.type === "file") {
          const files = event.target.files;
          if (files.length > 0) {
            value = Array.from(files).map((file) => ({
              name: file.name,
              type: file.type,
              size: file.size,
            }));
          }
        } else {
          value =
            event.target.type === "checkbox" || event.target.type === "radio"
              ? event.target.checked
              : event.target.value;
        }

        if (this.page.onChangeSubscriptions[id]) {
          Promise.all(this.page.onChangeSubscriptions[id].map((f) => f(value)));
        }
      }
    };

    handleOnSubmit = (event) => {
      if (event.target.tagName === "FORM") {
        const formId = event.target.id;
        if (this.page.onSubmitSubscriptions[formId] !== undefined) {
          this.page.onSubmitSubscriptions[formId](event);
        } else {
          console.warn(`No submit handlers for form with ID: ${formId}`);
        }
      }
    };
  }

  app = new NikApp();
  window.addEventListener("DOMContentLoaded", () => {
    document.addEventListener("click", app.handleClick);
    window.addEventListener("popstate", app.handlePopState);
    document.addEventListener("input", debounce(app.handleOnChange, 0));
    document.addEventListener("submit", app.handleOnSubmit);
  });
  window.__nik__ = app;
})();
