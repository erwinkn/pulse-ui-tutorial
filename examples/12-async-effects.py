import pulse as ps
import asyncio

class AsyncEffectState(ps.State):
    running: bool = False
    step: int = 0

    @ps.effect(lazy=True)
    async def ticker(self):
        # Simulate writes across awaits
        await asyncio.sleep(0.5)
        with ps.Untrack():
            self.step += 1
            self.step += 1
        await asyncio.sleep(0.5)
        # Keep going by rescheduling itself through a signal
        self.step += 1

    def start(self):
        # Manually schedule an effect
        self.ticker.schedule()
        self.running = True

    def stop(self):
        self.ticker.cancel()
        self.running = False


@ps.component
def AsyncEffectDemo():
    state = ps.states(AsyncEffectState)

    return ps.div(
        ps.div(
            ps.button(
                "Start async effect", onClick=state.start, className="btn-secondary"
            ),
            ps.button("Stop", onClick=state.stop, className="btn-secondary ml-2"),
            className="mb-2",
        ),
        ps.p(f"Running: {state.running}", className="text-sm"),
        ps.p(f"Step: {state.step}", className="text-sm"),
    )