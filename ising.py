import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import Normalize
from matplotlib.ticker import StrMethodFormatter

from lattice import Lattice

plt.rcParams.update({"figure.autolayout": True})


class Ising:
    def __init__(
        self,
        shape=(30, 30),
        temp=2.0,
        j=(1.0, 1.0),
        field=0.0,
        init_state="random",
    ) -> None:

        # Saving given init_state to include in __str__
        if init_state == "up":
            self._init_state = "up"
        elif init_state == "down":
            self._init_state = "down"
        else:
            self._init_state = "random"

        self.lattice = Lattice(shape, temp, j, field, init_state)
        self._energy = self.lattice.energy
        self._mag_mom = self.lattice.mag_mom
        self.mean_energy_hist = []
        self.magnet_hist = []
        self.specific_heat_hist = []
        self.susceptibility_hist = []

    def __repr__(self) -> str:
        return (
            f"Ising(shape={self.lattice.shape.__str__()}, "
            + f"temp={self.lattice.temp}, "
            + f"j={self.lattice.j.__str__()}, "
            + f"field={self.lattice.field})"
        )

    def __str__(self) -> str:
        return (
            f"Ising Model with Temperature {self.lattice.temp} and Field {self.lattice.field}, "
            + f"starting with {self.init_state} spins"
        )

    @property
    def init_state(self):
        return self._init_state

    @property
    def gen(self):
        return self.lattice._gen

    @property
    def energy(self):
        return self.lattice.energy

    @property
    def mag_mom(self):
        return self.lattice.mag_mom

    def update(self):
        self.mean_energy_hist.append(self.lattice.mean_energy())
        self.magnet_hist.append(self.lattice.magnet())
        self.specific_heat_hist.append(self.lattice.specific_heat())
        self.susceptibility_hist.append(self.lattice.susceptibility())
        self.lattice.update()


class AnimatedIsing(Ising):
    def __init__(
        self,
        shape=(30, 30),
        temp=2,
        j=(1, 1),
        field=0,
        init_state="random",
        time_series=False,
        interval=100,
        frames=60,
    ) -> None:

        super().__init__(
            shape=shape,
            temp=temp,
            j=j,
            field=field,
            init_state=init_state,
        )

        self.time_series = bool(time_series)
        self._time = 0
        self.time_hist = []

        if self.time_series:
            self.fig, self.ax = plt.subplots(3, 2)
            self.fig.set_size_inches(10.8, 7.2)

            # Merging axis [0, 0] and [1, 0]
            gridspec = self.ax[0, 0].get_gridspec()
            for ax in self.ax[0:2, 0]:
                ax.remove()

            self.fig.add_subplot(gridspec[0:2, 0])
            self.ax = self.fig.get_axes()  # ax[0, 0] is now ax[4]

            self.__update_animation = self.__update_ani_time_series
            self.__init_animation = self.__init_ani_time_series
        else:
            self.fig, self.ax = plt.subplots()
            self.__update_animation = self.__update_ani_no_time_series
            self.__init_animation = self.__init_ani_no_time_series

        self.fig.suptitle(self.__str__())

        self.interval = interval
        self.frames = frames

        self.animation = FuncAnimation(
            self.fig,
            func=self.__update_animation,
            init_func=self.__init_animation,
            interval=self.interval,
            save_count=self.frames,
        )

        self.axes_labels = {
            "time": r"$t$",
            "energy": r"$\langle E \rangle$",
            "magnet": r"$\langle \mu \rangle$",
            "specific_heat": r"$C$",
            "susceptibility": r"$\chi$",
        }

    def __repr__(self) -> str:
        return (
            f"AnimatedIsing(shape={self.lattice.shape.__str__()}, "
            + f"temp={self.lattice.temp}, "
            + f"j={self.lattice.j.__str__()}, "
            + f"field={self.lattice.field}, "
            + f"time_series={self.time_series}, "
            + f"interval={self.interval}, "
            + f"frames={self.frames})"
        )

    @property
    def time(self):
        return self.gen * self.interval / 1000

    def update(self):
        super().update()
        self.time_hist.append(self.time)

    def __set_axes(self):
        for ax in self.ax[:-1]:
            ax.yaxis.set_major_formatter(StrMethodFormatter("{x:.1e}"))
            ax.set(
                xlim=(0, self.frames * self.interval / 1000),
                xlabel=self.axes_labels["time"],
            )
            ax.grid(linestyle=":")

        self.ax[0].set(ylabel=self.axes_labels["energy"])
        self.ax[1].set(ylabel=self.axes_labels["magnet"])
        self.ax[2].set(ylabel=self.axes_labels["specific_heat"])
        self.ax[3].set(ylabel=self.axes_labels["susceptibility"])
        self.ax[4].set(ylabel="i", xlabel="j")

    def __init_ani_time_series(self):
        self.ax[4].imshow(self.lattice.state, norm=Normalize(vmin=-1.0, vmax=1.0))
        self.__set_axes()
        self.update()

    def __update_ani_time_series(self, frame):
        for ax in self.ax:
            ax.clear()

        self.__set_axes()
        self.ax[0].plot(self.time_hist, self.mean_energy_hist, color="purple")
        self.ax[1].plot(self.time_hist, self.magnet_hist, color="purple")
        self.ax[2].plot(self.time_hist, self.specific_heat_hist, color="purple")
        self.ax[3].plot(self.time_hist, self.susceptibility_hist, color="purple")
        self.ax[4].imshow(self.lattice.state, norm=Normalize(vmin=-1.0, vmax=1.0))
        self.update()

    def __init_ani_no_time_series(self):
        self.ax.imshow(self.lattice.state, norm=Normalize(vmin=-1.0, vmax=1.0))
        self.update()

    def __update_ani_no_time_series(self, frame):
        self.ax.clear()
        self.ax.imshow(self.lattice.state, norm=Normalize(vmin=-1.0, vmax=1.0))
        self.update()


if __name__ == "__main__":
    ising = AnimatedIsing(shape=(128, 128), temp=5.0, init_state="down")
    ising_time_series = AnimatedIsing(shape=(128, 128), temp=1.5, time_series=True)
    ising.animation.save("images/test.gif")
    ising_time_series.animation.save("images/test_time_series.gif")
