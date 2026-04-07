 battle_time)
                        if gate_wait > 0:
                            ult_text = f"ULT LOCK {gate_wait:.1f}s | {purple_text}"
                            ult_color = (100, 100, 100)
                        elif circle.ultimate_cooldown_timer <= 0:
                            ult_text = f"ULTIMATE READY | {purple_text}"
                            ult_color 