from flask import Flask, render_template, redirect, request
from paper_trade_app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug="True") 