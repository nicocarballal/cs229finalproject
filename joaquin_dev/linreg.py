import numpy as np
import util
import matplotlib.pyplot as plt


def main(train_path, test_path):
    """Problem: Poisson regression with gradient ascent.

    Args:
        lr: Learning rate for gradient ascent.
        train_path: Path to CSV file containing dataset for training.
        eval_path: Path to CSV file containing dataset for evaluation.
        save_path: Path to save predictions.
    """
    # Load training set
    x_train, y_train = util.load_dataset(train_path, label_col='y_burn', add_intercept=True)

    # *** START CODE HERE ***
    #
    my_model = LinearRegression()
    my_model.fit(x_train, y_train)
    #
    x_test, y_test = util.load_dataset(test_path, label_col='y_burn', add_intercept=True)
    y_predict = my_model.predict(x_test)

    # Plot results
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for i, y in enumerate(y_predict):
        if y:
            x = x_test[2]  # long
            y = x_test[3]  # lat
            z = x_test[1]  # day
            ax.scatter(x, y, z, c='r')

    ax.view_init(elev=0, azim=0)
    ax.set_title('iso view')

    plt.show()
    # *** END CODE HERE ***


class LinearRegression(object):
    """Poisson Regression.

    Example usage:
        > clf = PoissonRegression(step_size=lr)
        > clf.fit(x_train, y_train)
        > clf.predict(x_eval)
    """

    def __init__(self, theta=None):
        """
        Args:
            step_size: Step size for iterative solvers only.
            max_iter: Maximum number of iterations for the solver.
            eps: Threshold for determining convergence.
            theta_0: Initial guess for theta. If None, use the zero vector.
            verbose: Print loss values during training.
        """
        self.theta = theta

    def fit(self, X, y):
        """Run gradient ascent to maximize likelihood for Poisson regression.

        Args:
            x: Training example inputs. Shape (n_examples, dim).
            y: Training example labels. Shape (n_examples,).
        """
        # *** START CODE HERE ***
        self.theta = np.linalg.solve(np.dot(np.transpose(X), X), np.dot(np.transpose(X), y))
        # *** END CODE HERE ***

    def predict(self, x):
        """Make a prediction given inputs x.

        Args:
            x: Inputs of shape (n_examples, dim).

        Returns:
            Floating-point prediction for each input, shape (n_examples,).
        """
        # *** START CODE HERE ***
        predictions = np.dot(x,self.theta)
        return predictions
        # *** END CODE HERE ***


if __name__ == '__main__':
    main(train_path='fire_data_train.csv',
        test_path='fire_data_test.csv')
