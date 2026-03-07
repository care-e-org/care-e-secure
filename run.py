from app import create_app

app = create_app()

if __name__ == '__main__':
    # Running on 0.0.0.0 so you can potentially view it from another device on your local network
    app.run(host='127.0.0.1', port=5000)
