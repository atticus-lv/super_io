import time

from .core import get_pref, MeasureTime


class DynamicImport:
    # define exec
    def execute(self, context):
        # use pre-define index to call config
        ITEM = self.ITEM

        op_callable, ops_args, op_context = ITEM.get_operator_and_args()

        if op_callable:
            with MeasureTime() as start_time:
                for file_path in self.file_list:
                    if file_path in self.match_file_op_dict: continue
                    ops_args['filepath'] = file_path
                    try:
                        if op_context:
                            op_callable(op_context, **ops_args)
                        else:
                            op_callable(**ops_args)
                    except Exception as e:
                        self.report({"ERROR"}, str(e))

                if get_pref().report_time: self.report({"INFO"},
                                                       f'{self.bl_label} Cost {round(time.time() - start_time, 5)} s')
        else:
            self.report({"ERROR"}, f'{op_callable} Error!!!')

        return {"FINISHED"}
