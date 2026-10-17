"""Single entry point for the GUI and its background encoder process."""
import sys

def main():
    if len(sys.argv)>1 and sys.argv[1]=='--encode':
        if len(sys.argv)<5 or sys.argv[2]!='--log-file':raise SystemExit(2)
        log_path=sys.argv[3];sys.argv=[sys.argv[0]]+sys.argv[4:]
        with open(log_path,'w',encoding='utf-8',buffering=1) as stream:
            sys.stdout=sys.stderr=stream
            try:
                from encode import main as encode_main
                encode_main()
            except SystemExit:raise
            except Exception:
                import traceback
                traceback.print_exc();raise SystemExit(1)
    else:
        from encoder_ui import main as gui_main
        gui_main()

if __name__=='__main__':main()
