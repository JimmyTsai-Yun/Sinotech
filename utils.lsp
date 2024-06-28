; create print hellow word function
(defun hello_world ()
  (princ "Hellow, World!"))

; use the function
(defun wtype_selection ( / wtype)
  (setq option '("Diaphragm" "SheetPile" "BoredPile"))
  (setq dcl_id (load_dialog "dcl\\dtype_selection.dcl"))
  (if (not (new_dialog "dtype_selection" dcl_id)) (exit))
  (start_list "selections")
  (mapcar 'add_list option)
  (end_list)
  (action_tile "accept"
  (strcat
  "(progn"
  "(setq selected_option (atof (get_tile \"selections\")))"
  "(done_dialog) (setq userclick T))"
  ))
  (action_tile "cancel"
  (strcat
  "(quit)"
  ))
  (start_dialog)
  (unload_dialog dcl_id)
  (setq selected_option (fix selected_option))
  (setq selected_option (nth selected_option option))
  (setq wtype selected_option)
)